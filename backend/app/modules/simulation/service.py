from sqlalchemy.orm import Session
from app.modules.simulation import engine
from app.modules.simulation.models import SimulationRun, ScenarioType
from app.modules.simulation.schemas import SimulationRequest, SimulationResultOut, SalaryChangeParams, HeadcountChangeParams, LeavePolicyChangeParams

def run_simulation(db: Session, user_id: int, request: SimulationRequest) -> SimulationResultOut:
    scenario = request.scenario_type
    params = request.params
    warnings = []

    if scenario == ScenarioType.SALARY_CHANGE:
        typed = SalaryChangeParams(**params)
        try:
            from app.modules.payroll import calculators
        except ImportError:
            calculators = None
            warnings.append("payroll.calculators not yet available — using 80% estimate")
        impact = engine.simulate_salary_change(typed, calculators)

    elif scenario == ScenarioType.HEADCOUNT_CHANGE:
        typed = HeadcountChangeParams(**params)
        avg_salary = float(params.get("avg_salary_for_new_hires", 50000.0))
        impact = engine.simulate_headcount_change(typed, avg_salary)

    elif scenario == ScenarioType.LEAVE_POLICY_CHANGE:
        typed = LeavePolicyChangeParams(**params)
        avg_daily = float(params.get("avg_daily_salary", 2000.0))
        impact = engine.simulate_leave_policy_change(typed, avg_daily)

    else:
        raise ValueError(f"Unsupported scenario_type: {scenario}")

    run = SimulationRun(
        requested_by=user_id,
        scenario_type=scenario,
        input_params_json=params,
        result_json=impact
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return SimulationResultOut(
        scenario_type=scenario,
        summary=_build_summary(scenario, impact),
        impact=impact,
        warnings=warnings,
        run_id=run.id
    )

def _build_summary(scenario: ScenarioType, impact: dict) -> str:
    if scenario == ScenarioType.SALARY_CHANGE:
        delta = impact["monthly_cost_delta"]
        direction = "increase" if delta > 0 else "decrease"
        return f"Monthly cost {direction} of ₹{abs(delta):,.2f} (₹{abs(impact['annual_cost_delta']):,.2f}/yr)"
    elif scenario == ScenarioType.HEADCOUNT_CHANGE:
        return f"Headcount change of {impact['headcount_delta']} adds ₹{impact['annual_cost_delta']:,.2f}/yr"
    elif scenario == ScenarioType.LEAVE_POLICY_CHANGE:
        return f"Policy change {impact['direction']}s liability by ₹{abs(impact['annual_liability_delta']):,.2f}/yr"
    return "Simulation complete"

def get_history(db: Session, user_id: int) -> list[SimulationRun]:
    return db.query(SimulationRun).filter_by(requested_by=user_id).order_by(SimulationRun.created_at.desc()).all()
