from sqlalchemy import Column, Integer, DateTime, Enum, JSON, ForeignKey, func
from app.core.database import Base
import enum

class ScenarioType(str, enum.Enum):
    SALARY_CHANGE = "SALARY_CHANGE"
    HEADCOUNT_CHANGE = "HEADCOUNT_CHANGE"
    LEAVE_POLICY_CHANGE = "LEAVE_POLICY_CHANGE"
    ATTRITION_RISK = "ATTRITION_RISK"

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_type = Column(Enum(ScenarioType), nullable=False)
    input_params_json = Column(JSON, nullable=False)    # full input snapshot (no FK to other tables)
    result_json = Column(JSON, nullable=False)          # full result snapshot
    created_at = Column(DateTime, server_default=func.now())
    # IMPORTANT: No FK into employee/payroll/leave — inputs are COPIED, not referenced
