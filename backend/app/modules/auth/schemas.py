from pydantic import BaseModel, EmailStr
from app.modules.auth.models import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    role: Role
    employee_id: int | None = None

    model_config = {"from_attributes": True}
