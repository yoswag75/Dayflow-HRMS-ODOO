from sqlalchemy.orm import Session
from app.modules.auth.models import User, Role
from app.modules.auth.schemas import TokenPair
from app.core.security import verify_password, hash_password, create_access_token


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, email: str, password: str, role: Role = Role.EMPLOYEE) -> User:
    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_tokens(user: User) -> TokenPair:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenPair(access_token=token)
