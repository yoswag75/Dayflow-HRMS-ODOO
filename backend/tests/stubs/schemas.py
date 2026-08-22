from pydantic import BaseModel

class AttendanceSummaryOut(BaseModel):
    employee_id: int
    total_present: int
    total_absent: int
    streak_days: int
