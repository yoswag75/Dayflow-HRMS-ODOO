import calendar
from datetime import date, datetime, timedelta, timezone

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
    for employee in db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE).all():
        salary = db.query(SalaryStructure).filter(SalaryStructure.employee_id == employee.id).first()
        if not salary:
            continue
        summary = get_attendance_summary(db, employee.id, month=month, year=year)
        gross = calculate_gross(salary.basic, salary.hra, salary.allowances_json or {})
        deductions = calculate_deductions(salary.basic, working_days, summary.get("absent", 0))
        slip = Payslip(
            payroll_run_id=run.id,
            employee_id=employee.id,
            gross=gross,
            deductions_json={key: str(value) for key, value in deductions.items()},
            net_pay=calculate_net(gross, deductions),
        )
        db.add(slip)
        payslips.append(slip)
    run.status = "PROCESSED"
    run.processed_at = datetime.now(timezone.utc)
    db.commit()
    output = PayrollRunOut.model_validate(run)
    output.payslips = [PayslipOut.model_validate(slip) for slip in payslips]
    return output


def request_salary_change(db: Session, employee_id: int, payload: dict, requested_by: int):
    data = ChangeRequestCreate(
        entity_type="salary_structure",
        entity_id=employee_id,
        payload=payload,
        effective_date=date.today() + timedelta(days=30),
    )
    return create_change_request(db, data, requested_by=requested_by)


def get_latest_payslip(db: Session, employee_id: int):
    return db.query(Payslip).filter(Payslip.employee_id == employee_id).order_by(Payslip.generated_at.desc()).first()


def _apply_salary_change(db: Session, request) -> None:
    salary = db.query(SalaryStructure).filter(SalaryStructure.employee_id == request.entity_id).first()
    if not salary:
        raise ValueError(f"SalaryStructure for employee {request.entity_id} not found")
    for field, value in request.payload.items():
        setattr(salary, field, value)
    db.commit()


register_applier("salary_structure", _apply_salary_change)
