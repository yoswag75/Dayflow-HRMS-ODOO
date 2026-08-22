from datetime import date
from pydantic import BaseModel


class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    status: str
    reason: str | None = None
    resolved_by: int | None = None

    model_config = {"from_attributes": True}


class LeaveBalanceOut(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    balance: int

    model_config = {"from_attributes": True}
