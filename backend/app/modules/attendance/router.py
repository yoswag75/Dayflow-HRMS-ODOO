from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.modules.attendance.schemas import AttendanceRecordOut
from app.modules.attendance.service import clock_in, clock_out, get_all_attendance_for_period, get_attendance_for_period

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in", response_model=AttendanceRecordOut, status_code=201)
def do_clock_in(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    try:
        return clock_in(db, employee_id=user.employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-out", response_model=AttendanceRecordOut)
def do_clock_out(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    try:
        return clock_out(db, employee_id=user.employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=list[AttendanceRecordOut])
def my_attendance(start: date | None = None, end: date | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    end = end or date.today()
    start = start or end - timedelta(days=30)
    return get_attendance_for_period(db, user.employee_id, start, end)


@router.get("", response_model=list[AttendanceRecordOut])
def all_attendance(start: date | None = None, end: date | None = None, db: Session = Depends(get_db), _=Depends(require_admin)):
    end = end or date.today()
    start = start or end - timedelta(days=30)
    return get_all_attendance_for_period(db, start, end)
