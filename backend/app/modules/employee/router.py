from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.modules.employee.schemas import EmployeeCreate, EmployeeOnboardOut, EmployeeOut
from app.modules.employee.service import get_employee_by_id, list_employees, onboard_employee

router = APIRouter(prefix="/employees", tags=["Employee"])


@router.post("", response_model=EmployeeOnboardOut, status_code=201)
def create(body: EmployeeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    emp, temp_password = onboard_employee(db, body)
    return EmployeeOnboardOut(employee=emp, temp_password=temp_password)


@router.get("", response_model=list[EmployeeOut])
def list_all(department: str | None = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return list_employees(db, department=department)


@router.get("/{id}", response_model=EmployeeOut)
def get_one(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    emp = get_employee_by_id(db, id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp
