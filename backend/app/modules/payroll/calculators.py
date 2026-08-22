from decimal import Decimal


def calculate_gross(basic: int, hra: int, allowances: dict) -> Decimal:
    return Decimal(basic) + Decimal(hra) + sum(Decimal(v) for v in allowances.values())


def calculate_deductions(basic: int, working_days: int, unpaid_absent_days: int) -> dict:
    per_day = Decimal(basic) / Decimal(working_days) if working_days else Decimal(0)
    return {"unpaid_leave": per_day * unpaid_absent_days}


def calculate_net(gross: Decimal, deductions: dict) -> Decimal:
    return gross - sum(deductions.values())
