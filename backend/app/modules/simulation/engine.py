from app.modules.simulation.schemas import SalaryChangeParams, HeadcountChangeParams, LeavePolicyChangeParams

def simulate_salary_change(params: SalaryChangeParams, calculators=None) -> dict:
    """
    calculators = Dev A's payroll.calculators module (dependency-injected).
    If None (not yet available), uses 80% net-of-gross estimate.
    """
    if calculators:
        current_net = calculators.compute_net(params.current_gross, params.proposed_breakdown)
        proposed_net = calculators.compute_net(params.proposed_gross, params.proposed_breakdown)
    else:
        current_net = params.current_gross * 0.80
        proposed_net = params.proposed_gross * 0.80

    monthly_delta = proposed_net - current_net
    return {
        "current_gross": params.current_gross,
        "proposed_gross": params.proposed_gross,
        "current_net": round(current_net, 2),
        "proposed_net": round(proposed_net, 2),
        "monthly_cost_delta": round(monthly_delta, 2),
        "annual_cost_delta": round(monthly_delta * 12, 2),
    }

def simulate_headcount_change(params: HeadcountChangeParams, avg_salary: float) -> dict:
    monthly_cost_delta = params.delta * avg_salary
    return {
        "department": params.department,
        "headcount_delta": params.delta,
        "avg_salary": avg_salary,
        "monthly_cost_delta": round(monthly_cost_delta, 2),
        "annual_cost_delta": round(monthly_cost_delta * 12, 2),
    }

def simulate_leave_policy_change(params: LeavePolicyChangeParams, avg_daily_salary: float) -> dict:
    day_delta = params.proposed_days - params.current_days
    annual_liability_delta = day_delta * avg_daily_salary
    return {
        "leave_type": params.leave_type,
        "current_days": params.current_days,
        "proposed_days": params.proposed_days,
        "day_delta": day_delta,
        "annual_liability_delta": round(annual_liability_delta, 2),
        "direction": "increase" if day_delta > 0 else "decrease",
    }
