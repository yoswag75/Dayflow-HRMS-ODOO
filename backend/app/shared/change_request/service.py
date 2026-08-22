from datetime import date, datetime, timezone
from typing import Callable
from sqlalchemy.orm import Session
from app.shared.change_request.models import ChangeRequest
from app.shared.change_request.schemas import ChangeRequestCreate, ChangeRequestOut

APPLIER_REGISTRY: dict[str, Callable] = {}


def register_applier(entity_type: str, fn: Callable) -> None:
    APPLIER_REGISTRY[entity_type] = fn


def create_change_request(db: Session, data: ChangeRequestCreate, requested_by: int) -> ChangeRequestOut:
    cr = ChangeRequest(**data.model_dump(), requested_by=requested_by)
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return ChangeRequestOut.model_validate(cr)


def get_due_change_requests(db: Session, as_of: date | None = None) -> list[ChangeRequestOut]:
    as_of = as_of or date.today()
    rows = db.query(ChangeRequest).filter(
        ChangeRequest.status == "PENDING",
        ChangeRequest.effective_date <= as_of,
    ).all()
    return [ChangeRequestOut.model_validate(r) for r in rows]


def run_due_change_requests(db: Session, as_of: date | None = None) -> None:
    for cr in get_due_change_requests(db, as_of):
        row = db.get(ChangeRequest, cr.id)
        applier = APPLIER_REGISTRY.get(cr.entity_type)
        try:
            if applier:
                applier(db, cr)
            row.status = "APPLIED"
            row.applied_at = datetime.now(timezone.utc)
        except Exception:
            row.status = "FAILED"
        db.commit()
