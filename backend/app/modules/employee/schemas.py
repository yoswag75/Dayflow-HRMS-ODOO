from datetime import date
from pydantic import BaseModel, EmailStr
from app.modules.employee.models import EmployeeStatus


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    designation: str | None = None
    department: str | None = None
    date_of_joining: date | None = None
    salary_band: str | None = None
    manager_id: int | None = None


class EmployeeUpdate(BaseModel):
    designation: str | None = None
    department: str | None = None
    salary_band: str | None = None
    manager_id: int | None = None
    status: EmployeeStatus | None = None


class EmployeeOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    designation: str | None = None
    department: str | None = None
    date_of_joining: date | None = None
    salary_band: str | None = None
    manager_id: int | None = None
    status: EmployeeStatus

    model_config = {"from_attributes": True}


class EmployeeOnboardOut(BaseModel):
    employee: EmployeeOut
    temp_password: str
