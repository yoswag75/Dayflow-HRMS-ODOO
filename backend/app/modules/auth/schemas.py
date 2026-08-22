from pydantic import BaseModel, EmailStr, Field
from app.modules.auth.models import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SetupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)


class PasswordChangeRequest(BaseModel):
    password: str = Field(min_length=10)


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    role: Role
    employee_id: int | None = None
    force_password_change: bool = False

    model_config = {"from_attributes": True}
