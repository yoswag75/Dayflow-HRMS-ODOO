from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional, List

class ScenarioType(str, Enum):
    SALARY_CHANGE = "SALARY_CHANGE"
    HEADCOUNT_CHANGE = "HEADCOUNT_CHANGE"
    LEAVE_POLICY_CHANGE = "LEAVE_POLICY_CHANGE"
    ATTRITION_RISK = "ATTRITION_RISK"

# --- SCENARIO PARAM SCHEMAS ---
class SalaryChangeParams(BaseModel):
    employee_id: int
    current_gross: float
    proposed_gross: float
    proposed_breakdown: dict  # {"basic": 0.5, "hra": 0.2, "allowances": 0.3}

class HeadcountChangeParams(BaseModel):
    department: str
    delta: int               # +5 = hire 5, -2 = reduce by 2
    avg_salary_for_new_hires: Optional[float] = None

class LeavePolicyChangeParams(BaseModel):
    leave_type: str          # "paid" | "sick"
    current_days: int
    proposed_days: int

# --- REQUEST / RESPONSE ---
class SimulationRequest(BaseModel):
    scenario_type: ScenarioType
    params: dict             # validated by engine per scenario_type

class SimulationResultOut(BaseModel):
    scenario_type: ScenarioType
    summary: str             # human-readable one-liner
    impact: dict             # {"monthly_cost_delta": 5000, "annual_cost_delta": 60000}
    warnings: List[str] = []
    run_id: Optional[int] = None

class SimulationRunOut(BaseModel):
    id: int
    scenario_type: ScenarioType
    input_params_json: dict
    result_json: dict
    created_at: datetime
    model_config = {"from_attributes": True}
