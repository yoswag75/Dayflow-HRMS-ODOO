import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modules.notification.models import Base, NotificationPreference, NotificationChannel
from app.modules.notification.schemas import NotificationCreate, NotificationType
from app.modules.notification import service
from app.modules.auth.models import User

# Create an in-memory SQLite database for tests
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_and_list_notification(db_session):
    notif = service.create_notification(db_session, NotificationCreate(
        user_id=1, title="Leave approved",
        body="Your leave was approved.", source_module="leave", type=NotificationType.INFO
    ))
    assert notif.id is not None
    results = service.list_notifications(db_session, user_id=1)
    assert len(results) == 1
    assert results[0].read is False

def test_mark_read(db_session):
    notif = service.create_notification(db_session, NotificationCreate(
        user_id=1, title="Test", body="Test body", source_module="test", type=NotificationType.INFO
    ))
    updated = service.mark_read(db_session, notif.id, user_id=1)
    assert updated.read is True

def test_mark_read_wrong_user_raises(db_session):
    notif = service.create_notification(db_session, NotificationCreate(
        user_id=1, title="Test", body="Test", source_module="test", type=NotificationType.INFO
    ))
    with pytest.raises(ValueError):
        service.mark_read(db_session, notif.id, user_id=99)  # wrong user

def test_upsert_preference(db_session):
    pref = service.upsert_preference(db_session, user_id=1, channel=NotificationChannel.EMAIL, enabled=False)
    assert pref.enabled is False
    
    # Update existing
    pref2 = service.upsert_preference(db_session, user_id=1, channel=NotificationChannel.EMAIL, enabled=True)
    assert pref.id == pref2.id
    assert pref2.enabled is True
