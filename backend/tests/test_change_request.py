from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.shared.change_request.schemas import ChangeRequestCreate
from app.shared.change_request.service import (
    create_change_request, get_due_change_requests,
    register_applier, run_due_change_requests,
)


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_create_change_request():
    db = make_db()
    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=1,
        payload={"field": "value"},
        effective_date=date.today(),
    )
    cr = create_change_request(db, data, requested_by=1)
    assert cr.id is not None
    assert cr.status == "PENDING"


def test_run_due_applies_pending():
    db = make_db()
    applied = []

    def fake_applier(db, cr):
        applied.append(cr.entity_id)

    register_applier("test_entity", fake_applier)

    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=42,
        payload={"x": 1},
        effective_date=date.today(),
    )
    create_change_request(db, data, requested_by=1)
    run_due_change_requests(db)

    assert 42 in applied


def test_future_cr_not_applied():
    db = make_db()
    applied = []
    register_applier("test_entity", lambda db, cr: applied.append(cr.id))

    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=99,
        payload={},
        effective_date=date.today() + timedelta(days=30),
    )
    create_change_request(db, data, requested_by=1)
    run_due_change_requests(db)
    assert applied == []


def test_applied_cr_not_rerun():
    db = make_db()
    call_count = [0]
    register_applier("test_entity", lambda db, cr: call_count.__setitem__(0, call_count[0] + 1))

    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=7,
        payload={},
        effective_date=date.today(),
    )
    create_change_request(db, data, requested_by=1)
    run_due_change_requests(db)
    run_due_change_requests(db)  # second run should not re-apply
    assert call_count[0] == 1
