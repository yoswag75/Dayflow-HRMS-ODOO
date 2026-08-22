import secrets

from sqlalchemy.orm import Session

from app.modules.employee.models import Employee
from app.modules.employee.schemas import EmployeeCreate, EmployeeOut


def create_employee(db: Session, data: EmployeeCreate) -> EmployeeOut:
    employee = Employee(**data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return EmployeeOut.model_validate(employee)


def get_employee_by_id(db: Session, employee_id: int) -> EmployeeOut | None:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    return EmployeeOut.model_validate(employee) if employee else None


def list_employees(db: Session, department: str | None = None) -> list[EmployeeOut]:
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    return [EmployeeOut.model_validate(employee) for employee in query.all()]


def get_all_active_employees(db: Session) -> list[EmployeeOut]:
    from app.modules.employee.models import EmployeeStatus

    rows = db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE).all()
    return [EmployeeOut.model_validate(employee) for employee in rows]


def onboard_employee(db: Session, data: EmployeeCreate) -> tuple[EmployeeOut, str]:
    from app.modules.auth.models import User
    from app.modules.auth.service import create_user
    from app.modules.leave.service import seed_balances
    from app.modules.onboarding.service import create_checklist

    employee = create_employee(db, data)
    temp_password = secrets.token_urlsafe(12)
    user = create_user(db, email=data.email, password=temp_password)
    db.query(User).filter(User.id == user.id).update({"employee_id": employee.id})
    db.query(Employee).filter(Employee.id == employee.id).update({"user_id": user.id})
    seed_balances(db, employee_id=employee.id)
    create_checklist(db, employee_id=employee.id, role=data.designation or "default")
    db.commit()
    linked = get_employee_by_id(db, employee.id)
    if not linked:
        raise RuntimeError("Employee onboarding failed")
    return linked, temp_password
