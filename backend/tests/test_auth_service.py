from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.auth.models import User, Role
from app.modules.auth.service import authenticate_user, create_user
from app.core.security import hash_password


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_authenticate_user_success():
    db = make_db()
    db.add(User(email="x@y.com", hashed_password=hash_password("pass"), role=Role.EMPLOYEE, is_active=True))
    db.commit()
    user = authenticate_user(db, "x@y.com", "pass")
    assert user is not None
    assert user.email == "x@y.com"


def test_authenticate_user_wrong_password():
    db = make_db()
    db.add(User(email="x@y.com", hashed_password=hash_password("pass"), role=Role.EMPLOYEE, is_active=True))
    db.commit()
    assert authenticate_user(db, "x@y.com", "wrong") is None


def test_authenticate_user_not_found():
    db = make_db()
    assert authenticate_user(db, "no@one.com", "pass") is None


def test_create_user_persists():
    db = make_db()
    user = create_user(db, email="new@dayflow.hr", password="secret", role=Role.HR)
    assert user.id is not None
    assert user.role == Role.HR


def test_inactive_user_not_authenticated():
    db = make_db()
    db.add(User(email="x@y.com", hashed_password=hash_password("pass"), role=Role.EMPLOYEE, is_active=False))
    db.commit()
    assert authenticate_user(db, "x@y.com", "pass") is None
