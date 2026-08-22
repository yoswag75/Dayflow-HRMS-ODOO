from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class EmployeeOut(BaseModel):
    id: int
    user_id: int
    name: str
    department: str
    designation: str
    date_of_joining: date

class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: date
    status: str
    check_in: Optional[datetime]
    check_out: Optional[datetime]

class AttendanceSummaryOut(BaseModel):
    employee_id: int
    total_present: int
    total_absent: int
    streak_days: int

class LeaveBalanceOut(BaseModel):
    employee_id: int
    paid_remaining: int
    sick_remaining: int
    unpaid_used: int

class PayslipOut(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    gross: float
    deductions: float
    net: float
    generated_at: datetime
