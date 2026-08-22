import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.leave.schemas import LeaveRequestCreate
from app.modules.leave.service import apply_leave, approve_leave, get_leave_balance, seed_balances


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_apply_leave_creates_pending():
    db = make_db()
    seed_balances(db, employee_id=1)
    req = LeaveRequestCreate(
        employee_id=1, leave_type="PAID",
        start_date="2026-09-01", end_date="2026-09-03", reason="Holiday"
    )
    result = apply_leave(db, req)
    assert result.status == "PENDING"


def test_approve_leave_deducts_balance():
    db = make_db()
    seed_balances(db, employee_id=1)
    req = LeaveRequestCreate(
        employee_id=1, leave_type="PAID",
        start_date="2026-09-01", end_date="2026-09-03", reason="Holiday"
    )
    leave = apply_leave(db, req)
    approve_leave(db, leave_id=leave.id, approver_id=99)
    balance = get_leave_balance(db, employee_id=1)
    paid = next(b for b in balance if b.leave_type == "PAID")
    assert paid.balance == 17  # 20 - 3 days


def test_insufficient_balance_raises():
    db = make_db()
    seed_balances(db, employee_id=1, paid_quota=1)
    req = LeaveRequestCreate(
        employee_id=1, leave_type="PAID",
        start_date="2026-09-01", end_date="2026-09-05", reason="Holiday"
    )
    leave = apply_leave(db, req)
    with pytest.raises(ValueError, match="Insufficient"):
        approve_leave(db, leave_id=leave.id, approver_id=99)


def test_reject_leave():
    db = make_db()
    seed_balances(db, employee_id=1)
    req = LeaveRequestCreate(
        employee_id=1, leave_type="SICK",
        start_date="2026-09-01", end_date="2026-09-01", reason="Unwell"
    )
    leave = apply_leave(db, req)
    from app.modules.leave.service import reject_leave
    rejected = reject_leave(db, leave_id=leave.id, approver_id=99)
    assert rejected.status == "REJECTED"


def test_unpaid_leave_approved_without_balance_check():
    db = make_db()
    seed_balances(db, employee_id=1)
    req = LeaveRequestCreate(
        employee_id=1, leave_type="UNPAID",
        start_date="2026-09-01", end_date="2026-09-30", reason="Sabbatical"
    )
    leave = apply_leave(db, req)
    result = approve_leave(db, leave_id=leave.id, approver_id=99)
    assert result.status == "APPROVED"
