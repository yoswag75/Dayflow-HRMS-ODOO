import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.modules.auth.models import User
# Import all models to ensure they are registered with Base.metadata
from app.modules.gamification.models import PointsLedger, Badge, EmployeeBadge
from app.modules.notification.models import NotificationPreference, NotificationChannel, Notification
from app.modules.chatbot.models import ChatSession, ChatMessage

@pytest.fixture
def db_session():
    # check_same_thread=False and StaticPool are required since asyncio.to_thread runs in another thread
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Setup baseline data
    user = User(id=1, email="test@dayflow.hr", hashed_password="stub")
    session.add(user)
    session.commit()
    
    yield session
    session.close()
