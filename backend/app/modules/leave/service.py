from sqlalchemy.orm import Session

from app.modules.leave.models import LeaveBalance, LeaveRequest
from app.modules.leave.schemas import LeaveBalanceOut, LeaveRequestCreate, LeaveRequestOut

DEFAULT_QUOTAS = {"PAID": 20, "SICK": 10, "UNPAID": 30, "EMERGENCY": 3}


def seed_balances(db: Session, employee_id: int, paid_quota: int = 20) -> None:
    quotas = {**DEFAULT_QUOTAS, "PAID": paid_quota}
    for leave_type, quota in quotas.items():
        db.add(LeaveBalance(employee_id=employee_id, leave_type=leave_type, balance=quota))
    db.commit()


def apply_leave(db: Session, data: LeaveRequestCreate) -> LeaveRequestOut:
    request = LeaveRequest(**data.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return LeaveRequestOut.model_validate(request)


def list_leave_requests(db: Session, employee_id: int | None = None) -> list[LeaveRequestOut]:
    query = db.query(LeaveRequest)
    if employee_id is not None:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    return [LeaveRequestOut.model_validate(request) for request in query.order_by(LeaveRequest.id.desc()).all()]


def approve_leave(db: Session, leave_id: int, approver_id: int) -> LeaveRequestOut:
    request = db.get(LeaveRequest, leave_id)
    if not request:
        raise ValueError("Leave request not found")
    days = (request.end_date - request.start_date).days + 1
    if request.leave_type != "UNPAID":
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == request.employee_id,
            LeaveBalance.leave_type == request.leave_type,
        ).first()
        if balance and balance.balance < days:
            raise ValueError(f"Insufficient {request.leave_type} balance")
        if balance:
            balance.balance -= days
    request.status = "APPROVED"
    request.resolved_by = approver_id
    db.commit()
    db.refresh(request)
    return LeaveRequestOut.model_validate(request)


def reject_leave(db: Session, leave_id: int, approver_id: int) -> LeaveRequestOut:
    request = db.get(LeaveRequest, leave_id)
    if not request:
        raise ValueError("Leave request not found")
    request.status = "REJECTED"
    request.resolved_by = approver_id
    db.commit()
    db.refresh(request)
    return LeaveRequestOut.model_validate(request)


def get_leave_balance(db: Session, employee_id: int) -> list[LeaveBalanceOut]:
    rows = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).all()
    return [LeaveBalanceOut.model_validate(row) for row in rows]
