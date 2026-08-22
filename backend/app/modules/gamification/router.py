from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.database import get_db
from app.modules.gamification import service, schemas
from app.modules.gamification.models import PointsLedger, EmployeeBadge

router = APIRouter(prefix="/gamification", tags=["gamification"])

@router.get(
    "/leaderboard", 
    response_model=list[schemas.LeaderboardEntryOut],
    summary="Get points leaderboard",
    description="Returns employees ranked by total points. Filterable by department and period (week/month).",
    responses={401: {"description": "Not authenticated"}, 200: {"description": "Ranked leaderboard"}}
)
def leaderboard(department: str = None, period: str = "month", db=Depends(get_db), _=Depends(get_current_user)):
    return service.get_leaderboard(db, department, period)

@router.get(
    "/me/points", 
    response_model=list[schemas.PointsLedgerOut],
    summary="Get my points history",
    description="Returns the points ledger history for the currently authenticated employee."
)
def my_points(db=Depends(get_db), current_user=Depends(get_current_user)):
    emp_id = getattr(current_user, "employee_id", current_user.id)
    entries = db.query(PointsLedger).filter_by(employee_id=emp_id).order_by(PointsLedger.created_at.desc()).all()
    return [schemas.PointsLedgerOut.model_validate(e) for e in entries]

@router.get(
    "/me/badges", 
    response_model=list[schemas.EmployeeBadgeOut],
    summary="Get my badges",
    description="Returns all badges unlocked by the currently authenticated employee."
)
def my_badges(db=Depends(get_db), current_user=Depends(get_current_user)):
    emp_id = getattr(current_user, "employee_id", current_user.id)
    return db.query(EmployeeBadge).filter_by(employee_id=emp_id).all()
