import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.attendance.service import clock_in, clock_out, get_attendance_for_period


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_clock_in_creates_record():
    db = make_db()
    record = clock_in(db, employee_id=1)
    assert record.id is not None
    assert record.check_in is not None
    assert record.check_out is None


def test_clock_out_sets_time():
    db = make_db()
    clock_in(db, employee_id=1)
    record = clock_out(db, employee_id=1)
    assert record.check_out is not None


def test_double_clock_in_raises():
    db = make_db()
    clock_in(db, employee_id=1)
    with pytest.raises(ValueError, match="already checked in"):
        clock_in(db, employee_id=1)


def test_clock_out_without_clock_in_raises():
    db = make_db()
    with pytest.raises(ValueError, match="No active check-in"):
        clock_out(db, employee_id=1)


def test_get_attendance_for_period():
    db = make_db()
    clock_in(db, employee_id=1)
    clock_out(db, employee_id=1)
    records = get_attendance_for_period(db, employee_id=1, start=date.today(), end=date.today())
    assert len(records) == 1
