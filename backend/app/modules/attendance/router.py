from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.attendance.schemas import AttendanceRecordOut
from app.modules.attendance.service import clock_in, clock_out, get_attendance_for_period

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/clock-in", response_model=AttendanceRecordOut, status_code=201)
def do_clock_in(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    try:
        return clock_in(db, employee_id=user.employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clock-out", response_model=AttendanceRecordOut)
def do_clock_out(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    try:
        return clock_out(db, employee_id=user.employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=list[AttendanceRecordOut])
def my_attendance(start: date, end: date, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    return get_attendance_for_period(db, user.employee_id, start, end)
