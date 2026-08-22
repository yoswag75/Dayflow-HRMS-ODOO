import pytest
from app.modules.simulation import engine
from app.modules.simulation.schemas import SalaryChangeParams, HeadcountChangeParams, LeavePolicyChangeParams

# Pure engine tests — zero fixtures
def test_salary_change_no_calculators():
    params = SalaryChangeParams(employee_id=1, current_gross=50000, proposed_gross=60000, proposed_breakdown={})
    result = engine.simulate_salary_change(params, calculators=None)
    assert result["monthly_cost_delta"] == pytest.approx(8000.0)
    assert result["annual_cost_delta"] == pytest.approx(96000.0)

def test_headcount_increase():
    params = HeadcountChangeParams(department="Engineering", delta=3)
    result = engine.simulate_headcount_change(params, avg_salary=60000)
    assert result["annual_cost_delta"] == 3 * 60000 * 12

def test_leave_policy_increase():
    params = LeavePolicyChangeParams(leave_type="paid", current_days=15, proposed_days=18)
    result = engine.simulate_leave_policy_change(params, avg_daily_salary=2000)
    assert result["day_delta"] == 3
    assert result["annual_liability_delta"] == 3 * 2000
    assert result["direction"] == "increase"
