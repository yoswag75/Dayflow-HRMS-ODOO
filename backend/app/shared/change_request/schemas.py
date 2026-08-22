from datetime import date, datetime
from pydantic import BaseModel


class ChangeRequestCreate(BaseModel):
    entity_type: str
    entity_id: int
    payload: dict
    effective_date: date


class ChangeRequestOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    payload: dict
    effective_date: date
    status: str
    requested_by: int
    approved_by: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
