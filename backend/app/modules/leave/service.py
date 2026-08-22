<<<<<<< HEAD
from sqlalchemy.orm import Session
from app.modules.leave.models import LeaveBalance, LeaveRequest
from app.modules.leave.schemas import LeaveRequestCreate, LeaveRequestOut, LeaveBalanceOut

DEFAULT_QUOTAS = {"PAID": 20, "SICK": 10, "UNPAID": 30, "EMERGENCY": 3}


def seed_balances(db: Session, employee_id: int, paid_quota: int = 20) -> None:
    quotas = {**DEFAULT_QUOTAS, "PAID": paid_quota}
    for leave_type, quota in quotas.items():
        db.add(LeaveBalance(employee_id=employee_id, leave_type=leave_type, balance=quota))
    db.commit()


def apply_leave(db: Session, data: LeaveRequestCreate) -> LeaveRequestOut:
    req = LeaveRequest(**data.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return LeaveRequestOut.model_validate(req)


def approve_leave(db: Session, leave_id: int, approver_id: int) -> LeaveRequestOut:
    req = db.get(LeaveRequest, leave_id)
    if not req:
        raise ValueError("Leave request not found")
    days = (req.end_date - req.start_date).days + 1
    if req.leave_type != "UNPAID":
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.leave_type == req.leave_type,
        ).first()
        if balance and balance.balance < days:
            raise ValueError(f"Insufficient {req.leave_type} balance")
        if balance:
            balance.balance -= days
    req.status = "APPROVED"
    req.resolved_by = approver_id
    db.commit()
    db.refresh(req)
    return LeaveRequestOut.model_validate(req)


def reject_leave(db: Session, leave_id: int, approver_id: int) -> LeaveRequestOut:
    req = db.get(LeaveRequest, leave_id)
    if not req:
        raise ValueError("Leave request not found")
    req.status = "REJECTED"
    req.resolved_by = approver_id
    db.commit()
    db.refresh(req)
    return LeaveRequestOut.model_validate(req)


def get_leave_balance(db: Session, employee_id: int) -> list[LeaveBalanceOut]:
    rows = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).all()
    return [LeaveBalanceOut.model_validate(r) for r in rows]
=======
def get_employee_by_id(db, id): pass
def get_leave_balance(db, id): pass
def get_latest_payslip(db, id): pass
>>>>>>> d80e6553fe1ed5dffcdd64aed8f583c84f9cd895
