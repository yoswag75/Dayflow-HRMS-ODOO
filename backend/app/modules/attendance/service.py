from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.attendance.schemas import AttendanceRecordOut


def clock_in(db: Session, employee_id: int) -> AttendanceRecordOut:
    today = date.today()
    existing = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date == today,
        AttendanceRecord.check_out == None,
    ).first()
    if existing:
        raise ValueError("Employee already checked in today")
    record = AttendanceRecord(
        employee_id=employee_id,
        date=today,
        check_in=datetime.now(timezone.utc),
        status=AttendanceStatus.PRESENT,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return AttendanceRecordOut.model_validate(record)


def clock_out(db: Session, employee_id: int) -> AttendanceRecordOut:
    today = date.today()
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date == today,
        AttendanceRecord.check_out == None,
    ).first()
    if not record:
        raise ValueError("No active check-in found")
    record.check_out = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return AttendanceRecordOut.model_validate(record)


def get_attendance_for_period(db: Session, employee_id: int, start: date, end: date) -> list[AttendanceRecordOut]:
    rows = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date >= start,
        AttendanceRecord.date <= end,
    ).all()
    return [AttendanceRecordOut.model_validate(r) for r in rows]


def get_all_attendance_for_period(db: Session, start: date, end: date) -> list[AttendanceRecordOut]:
    rows = db.query(AttendanceRecord).filter(
        AttendanceRecord.date >= start,
        AttendanceRecord.date <= end,
    ).order_by(AttendanceRecord.date.desc()).all()
    return [AttendanceRecordOut.model_validate(row) for row in rows]


def get_attendance_summary(db: Session, employee_id: int, month: int, year: int) -> dict:
    import calendar
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    records = get_attendance_for_period(db, employee_id, start, end)
    return {
        "present": sum(1 for r in records if r.status == AttendanceStatus.PRESENT),
        "absent": sum(1 for r in records if r.status == AttendanceStatus.ABSENT),
        "total_days": len(records),
    }
