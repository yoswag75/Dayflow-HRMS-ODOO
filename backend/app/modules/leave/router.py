from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.modules.leave.schemas import LeaveRequestCreate, LeaveRequestOut, LeaveBalanceOut
from app.modules.leave.service import apply_leave, approve_leave, reject_leave, get_leave_balance

router = APIRouter(prefix="/leave", tags=["Leave"])


@router.post("/apply", response_model=LeaveRequestOut, status_code=201)
def apply(body: LeaveRequestCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    body.employee_id = user.employee_id or body.employee_id
    return apply_leave(db, body)


@router.post("/{leave_id}/approve", response_model=LeaveRequestOut)
def approve(leave_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    try:
        return approve_leave(db, leave_id, approver_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{leave_id}/reject", response_model=LeaveRequestOut)
def reject(leave_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    try:
        return reject_leave(db, leave_id, approver_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance", response_model=list[LeaveBalanceOut])
def balance(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_leave_balance(db, user.employee_id)
