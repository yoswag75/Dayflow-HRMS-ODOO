<<<<<<< HEAD
import calendar
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.employee.models import Employee, EmployeeStatus
from app.modules.payroll.calculators import calculate_deductions, calculate_gross, calculate_net
from app.modules.payroll.models import PayrollRun, Payslip, SalaryStructure
from app.modules.payroll.schemas import PayrollRunOut, PayslipOut
from app.shared.change_request.schemas import ChangeRequestCreate
from app.shared.change_request.service import create_change_request, register_applier


def run_payroll(db: Session, month: int, year: int) -> PayrollRunOut:
    from app.modules.attendance.service import get_attendance_summary

    run = PayrollRun(month=month, year=year, status="DRAFT")
    db.add(run)
    db.commit()
    db.refresh(run)

    working_days = calendar.monthrange(year, month)[1]
    payslips = []

    employees = db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE).all()
    for emp in employees:
        salary = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp.id).first()
        if not salary:
            continue

        summary = get_attendance_summary(db, emp.id, month=month, year=year)
        absent_days = summary.get("absent", 0)

        gross = calculate_gross(salary.basic, salary.hra, salary.allowances_json or {})
        deductions = calculate_deductions(salary.basic, working_days, absent_days)
        net = calculate_net(gross, deductions)

        slip = Payslip(
            payroll_run_id=run.id,
            employee_id=emp.id,
            gross=gross,
            deductions_json={k: str(v) for k, v in deductions.items()},
            net_pay=net,
        )
        db.add(slip)
        payslips.append(slip)

    run.status = "PROCESSED"
    run.processed_at = datetime.now(timezone.utc)
    db.commit()

    out = PayrollRunOut.model_validate(run)
    out.payslips = [PayslipOut.model_validate(s) for s in payslips]
    return out


def request_salary_change(db: Session, employee_id: int, payload: dict, requested_by: int):
    data = ChangeRequestCreate(
        entity_type="salary_structure",
        entity_id=employee_id,
        payload=payload,
        effective_date=date.today() + timedelta(days=30),
    )
    return create_change_request(db, data, requested_by=requested_by)


def _apply_salary_change(db: Session, cr) -> None:
    salary = db.query(SalaryStructure).filter(SalaryStructure.employee_id == cr.entity_id).first()
    if not salary:
        raise ValueError(f"SalaryStructure for employee {cr.entity_id} not found")
    for field, value in cr.payload.items():
        setattr(salary, field, value)
    db.commit()


register_applier("salary_structure", _apply_salary_change)
=======
def get_employee_by_id(db, id): pass
def get_leave_balance(db, id): pass
def get_latest_payslip(db, id): pass
>>>>>>> d80e6553fe1ed5dffcdd64aed8f583c84f9cd895
