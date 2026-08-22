from datetime import date, datetime
from pydantic import BaseModel
from app.modules.attendance.models import AttendanceStatus


class AttendanceRecordOut(BaseModel):
    id: int
    employee_id: int
    date: date
    check_in: datetime | None
    check_out: datetime | None
    status: AttendanceStatus

    model_config = {"from_attributes": True}
