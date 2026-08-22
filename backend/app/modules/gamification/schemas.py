from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PointsLedgerOut(BaseModel):
    id: int
    employee_id: int
    points: int
    reason: str
    source_module: str
    created_at: datetime
    model_config = {"from_attributes": True}

class BadgeOut(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    model_config = {"from_attributes": True}

class EmployeeBadgeOut(BaseModel):
    badge: BadgeOut
    awarded_at: datetime
    model_config = {"from_attributes": True}

class LeaderboardEntryOut(BaseModel):
    rank: int
    employee_id: int
    employee_name: str
    total_points: int
    department: str
