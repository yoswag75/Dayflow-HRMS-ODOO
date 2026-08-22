from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import Role, User
from app.modules.auth.schemas import LoginRequest, PasswordChangeRequest, SetupRequest, TokenPair, UserOut
from app.modules.auth.service import authenticate_user, create_user, issue_tokens
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/setup-status")
def setup_status(db: Session = Depends(get_db)):
    return {"required": db.query(User).count() == 0}


@router.post("/setup", response_model=TokenPair, status_code=201)
def setup(body: SetupRequest, db: Session = Depends(get_db)):
    if db.query(User).count() != 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Initial setup has already been completed")
    user = create_user(db, body.email, body.password, role=Role.ADMIN)
    user.force_password_change = False
    db.commit()
    db.refresh(user)
    return issue_tokens(user)


@router.post("/login", response_model=TokenPair)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return issue_tokens(user)


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/change-password", response_model=TokenPair)
def change_password(body: PasswordChangeRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    current_user.hashed_password = hash_password(body.password)
    current_user.force_password_change = False
    db.commit()
    db.refresh(current_user)
    return issue_tokens(current_user)
