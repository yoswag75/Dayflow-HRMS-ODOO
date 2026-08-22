from sqlalchemy import Column, Integer, String, Date, DateTime, JSON, Numeric, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False, unique=True)
    basic = Column(Integer, nullable=False)
    hra = Column(Integer, default=0)
    allowances_json = Column(JSON, default={})
    effective_date = Column(Date, nullable=True)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    id = Column(Integer, primary_key=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(16), default="DRAFT", nullable=False)  # DRAFT/PROCESSED/PAID
    processed_at = Column(DateTime(timezone=True), nullable=True)


class Payslip(Base):
    __tablename__ = "payslips"
    id = Column(Integer, primary_key=True)
    payroll_run_id = Column(Integer, nullable=False)
    employee_id = Column(Integer, nullable=False)
    gross = Column(Numeric(12, 2), nullable=False)
    deductions_json = Column(JSON, default={})
    net_pay = Column(Numeric(12, 2), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
