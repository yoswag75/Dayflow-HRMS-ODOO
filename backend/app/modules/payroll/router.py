from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.modules.payroll.schemas import PayrollRunOut
from app.modules.payroll.service import run_payroll, request_salary_change

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.post("/run", response_model=PayrollRunOut)
def trigger_payroll(month: int, year: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    return run_payroll(db, month=month, year=year)


@router.post("/{employee_id}/salary-change")
def salary_change(employee_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(require_admin)):
    try:
        return request_salary_change(db, employee_id=employee_id, payload=payload, requested_by=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
