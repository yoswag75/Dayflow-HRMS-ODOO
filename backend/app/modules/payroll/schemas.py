from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class PayslipOut(BaseModel):
    id: int
    employee_id: int
    gross: Decimal
    deductions_json: dict
    net_pay: Decimal
    generated_at: datetime

    model_config = {"from_attributes": True}


class PayrollRunOut(BaseModel):
    id: int
    month: int
    year: int
    status: str
    payslips: list[PayslipOut] = []

    model_config = {"from_attributes": True}
