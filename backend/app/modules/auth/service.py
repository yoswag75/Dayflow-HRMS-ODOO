from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        employee_id=user_data.employee_id,
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_verified=False,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user