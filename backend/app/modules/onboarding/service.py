from sqlalchemy.orm import Session
from app.modules.onboarding.models import OnboardingTask
from app.modules.onboarding.schemas import OnboardingTaskOut

ROLE_TEMPLATES: dict[str, list[str]] = {
    "Engineer": ["Setup laptop", "Read codebase docs", "Meet your buddy", "Complete HR forms"],
    "HR": ["Read HR policy", "Setup accounts", "Meet your buddy", "Complete HR forms"],
    "default": ["Setup accounts", "Meet your buddy", "Complete HR forms"],
}


def create_checklist(db: Session, employee_id: int, role: str) -> list[OnboardingTaskOut]:
    task_names = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["default"])
    tasks = [
        OnboardingTask(employee_id=employee_id, task_name=name, role_template=role)
        for name in task_names
    ]
    db.add_all(tasks)
    db.commit()
    for t in tasks:
        db.refresh(t)
    return [OnboardingTaskOut.model_validate(t) for t in tasks]


def complete_task(db: Session, task_id: int) -> OnboardingTaskOut:
    task = db.query(OnboardingTask).filter(OnboardingTask.id == task_id).first()
    if not task:
        raise ValueError("Task not found")
    task.status = "DONE"
    db.commit()
    db.refresh(task)
    return OnboardingTaskOut.model_validate(task)


def get_status(db: Session, employee_id: int) -> dict:
    tasks = db.query(OnboardingTask).filter(OnboardingTask.employee_id == employee_id).all()
    done = sum(1 for t in tasks if t.status == "DONE")
    return {"total": len(tasks), "completed": done, "remaining": len(tasks) - done}
