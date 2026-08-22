import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    HR = "HR"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=True)  # FK to employees.id added via migration in Task 5
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True)
    force_password_change = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
