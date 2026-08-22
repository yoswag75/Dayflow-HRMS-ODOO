import enum
from sqlalchemy import Column, Integer, String, Date, Enum
from app.core.database import Base


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)  # FK to users.id added via migration when linked
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    designation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    date_of_joining = Column(Date, nullable=True)
    salary_band = Column(String(50), nullable=True)
    manager_id = Column(Integer, nullable=True)  # self-referential, FK added via migration
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
