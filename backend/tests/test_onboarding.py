from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.onboarding.service import create_checklist, complete_task, get_status


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_create_checklist():
    db = make_db()
    tasks = create_checklist(db, employee_id=1, role="Engineer")
    assert len(tasks) > 0
    assert all(t.status == "PENDING" for t in tasks)


def test_create_checklist_unknown_role_uses_default():
    db = make_db()
    tasks = create_checklist(db, employee_id=1, role="Unicorn")
    assert len(tasks) > 0


def test_complete_task():
    db = make_db()
    tasks = create_checklist(db, employee_id=1, role="Engineer")
    updated = complete_task(db, task_id=tasks[0].id)
    assert updated.status == "DONE"


def test_get_status():
    db = make_db()
    tasks = create_checklist(db, employee_id=1, role="Engineer")
    complete_task(db, task_id=tasks[0].id)
    status = get_status(db, employee_id=1)
    assert status["completed"] == 1
    assert status["total"] == len(tasks)
    assert status["remaining"] == len(tasks) - 1
