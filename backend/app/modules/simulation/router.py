from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.database import get_db
from app.modules.simulation import service, schemas

router = APIRouter(tags=["Simulation"])

@router.post("/simulation/run", response_model=schemas.SimulationResultOut)
def run_simulation(request: schemas.SimulationRequest, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return service.run_simulation(db, current_user.id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/simulation/history/{user_id}", response_model=list[schemas.SimulationRunOut])
def simulation_history(user_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    # Basic authorization check: a user can only see their own history unless they are an admin.
    # We assume `current_user` has `id` and optionally `is_admin`.
    is_admin = getattr(current_user, "is_admin", False)
    if current_user.id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return service.get_history(db, user_id)
