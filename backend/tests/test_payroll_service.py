from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.attendance.models import AttendanceRecord  # registers table with Base
from app.modules.employee.models import Employee, EmployeeStatus
from app.modules.payroll.models import SalaryStructure
from app.modules.payroll.service import run_payroll, request_salary_change


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def seed_employee_with_salary(db, basic=50000):
    emp = Employee(first_name="Test", last_name="User", email="t@dayflow.hr", status=EmployeeStatus.ACTIVE)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    sal = SalaryStructure(employee_id=emp.id, basic=basic, hra=0, allowances_json={})
    db.add(sal)
    db.commit()
    return emp


def test_run_payroll_generates_payslips():
    db = make_db()
    emp = seed_employee_with_salary(db, basic=50000)
    result = run_payroll(db, month=8, year=2026)
    assert result.status == "PROCESSED"
    assert len(result.payslips) == 1
    assert result.payslips[0].employee_id == emp.id
    assert result.payslips[0].gross == 50000


def test_salary_change_request_creates_cr():
    db = make_db()
    cr = request_salary_change(
        db, employee_id=1,
        payload={"basic": 60000},
        requested_by=99,
    )
    assert cr.entity_type == "salary_structure"
    assert cr.status == "PENDING"
    # effective_date must be today + 30
    from datetime import date, timedelta
    assert cr.effective_date == date.today() + timedelta(days=30)
