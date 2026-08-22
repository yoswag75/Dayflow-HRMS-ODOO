from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.modules.onboarding.models import OnboardingTask
from app.modules.onboarding.schemas import OnboardingTaskOut
from app.modules.onboarding.service import complete_task, get_status

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/me", response_model=list[OnboardingTaskOut])
def my_checklist(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee record")
    tasks = db.query(OnboardingTask).filter(OnboardingTask.employee_id == user.employee_id).all()
    return [OnboardingTaskOut.model_validate(t) for t in tasks]


@router.patch("/tasks/{task_id}", response_model=OnboardingTaskOut)
def mark_done(task_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return complete_task(db, task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{employee_id}", response_model=dict)
def employee_status(employee_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    return get_status(db, employee_id)
