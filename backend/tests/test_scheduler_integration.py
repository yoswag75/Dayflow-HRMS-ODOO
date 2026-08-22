from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.attendance.models import AttendanceRecord
from app.modules.employee.models import Employee, EmployeeStatus
from app.modules.payroll.models import SalaryStructure
from app.modules.payroll.service import run_payroll, request_salary_change
from app.core.scheduler import trigger_due_change_requests


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def seed(db, basic=50000):
    emp = Employee(first_name="Pay", last_name="Test", email="p@dayflow.hr", status=EmployeeStatus.ACTIVE)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    sal = SalaryStructure(employee_id=emp.id, basic=basic, hra=0, allowances_json={})
    db.add(sal)
    db.commit()
    return emp


def test_salary_change_applied_by_scheduler():
    db = make_db()
    emp = seed(db, basic=50000)

    # First payroll — uses original salary
    result1 = run_payroll(db, month=7, year=2026)
    assert result1.payslips[0].gross == Decimal("50000")

    # Request salary change (30-day rule enforced by service; bypass for test by patching effective_date)
    cr = request_salary_change(db, employee_id=emp.id, payload={"basic": 70000}, requested_by=99)

    from app.shared.change_request.models import ChangeRequest
    rec = db.get(ChangeRequest, cr.id)
    rec.effective_date = date.today()
    db.commit()

    # Simulate scheduler firing
    trigger_due_change_requests(db)

    # Second payroll — must pick up new salary
    result2 = run_payroll(db, month=8, year=2026)
    assert result2.payslips[0].gross == Decimal("70000")
