from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    employee_id: Optional[str] = None
    email: EmailStr
    username: str
    password: str
    role: str = "employee"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    employee_id: Optional[str] = None
    email: EmailStr
    username: str
    role: str
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"