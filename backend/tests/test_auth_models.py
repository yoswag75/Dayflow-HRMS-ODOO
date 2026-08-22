from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.auth.models import User, Role


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_create_user():
    db = make_session()
    u = User(email="test@dayflow.hr", hashed_password="hashed", role=Role.EMPLOYEE)
    db.add(u)
    db.commit()
    db.refresh(u)
    assert u.id is not None
    assert u.role == Role.EMPLOYEE


def test_user_defaults():
    db = make_session()
    u = User(email="admin@dayflow.hr", hashed_password="hashed", role=Role.ADMIN)
    db.add(u)
    db.commit()
    db.refresh(u)
    assert u.is_active is True
    assert u.force_password_change is True
    assert u.employee_id is None


def test_all_roles_exist():
    assert Role.ADMIN == "ADMIN"
    assert Role.HR == "HR"
    assert Role.MANAGER == "MANAGER"
    assert Role.EMPLOYEE == "EMPLOYEE"
