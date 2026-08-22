from decimal import Decimal
from app.modules.payroll.calculators import calculate_gross, calculate_deductions, calculate_net


def test_calculate_gross_basic_only():
    gross = calculate_gross(basic=50000, hra=0, allowances={})
    assert gross == Decimal("50000")


def test_calculate_gross_with_components():
    gross = calculate_gross(basic=50000, hra=10000, allowances={"travel": 5000})
    assert gross == Decimal("65000")


def test_calculate_deductions_unpaid_absent():
    deductions = calculate_deductions(basic=60000, working_days=30, unpaid_absent_days=1)
    assert deductions["unpaid_leave"] == Decimal("2000")  # 60000 / 30 = 2000 per day


def test_calculate_deductions_no_absence():
    deductions = calculate_deductions(basic=60000, working_days=30, unpaid_absent_days=0)
    assert deductions["unpaid_leave"] == Decimal("0")


def test_calculate_net():
    net = calculate_net(gross=Decimal("75000"), deductions={"unpaid_leave": Decimal("2000")})
    assert net == Decimal("73000")


def test_calculate_net_no_deductions():
    net = calculate_net(gross=Decimal("50000"), deductions={})
    assert net == Decimal("50000")
