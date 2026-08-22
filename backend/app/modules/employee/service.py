<<<<<<< HEAD
import secrets
from sqlalchemy.orm import Session
from app.modules.employee.models import Employee
from app.modules.employee.schemas import EmployeeCreate, EmployeeOut


def create_employee(db: Session, data: EmployeeCreate) -> EmployeeOut:
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return EmployeeOut.model_validate(emp)


def get_employee_by_id(db: Session, employee_id: int) -> EmployeeOut | None:
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    return EmployeeOut.model_validate(emp) if emp else None


def list_employees(db: Session, department: str | None = None) -> list[EmployeeOut]:
    q = db.query(Employee)
    if department:
        q = q.filter(Employee.department == department)
    return [EmployeeOut.model_validate(e) for e in q.all()]


def onboard_employee(db: Session, data: EmployeeCreate) -> tuple[EmployeeOut, str]:
    from app.modules.auth.service import create_user
    from app.modules.auth.models import User
    from app.modules.leave.service import seed_balances
    emp = create_employee(db, data)
    temp_password = secrets.token_urlsafe(12)
    user = create_user(db, email=data.email, password=temp_password)
    db.query(User).filter(User.id == user.id).update({"employee_id": emp.id})
    seed_balances(db, employee_id=emp.id)
    db.commit()
    return emp, temp_password
=======
def get_employee_by_id(db, id): pass
def get_leave_balance(db, id): pass
def get_latest_payslip(db, id): pass
>>>>>>> d80e6553fe1ed5dffcdd64aed8f583c84f9cd895
