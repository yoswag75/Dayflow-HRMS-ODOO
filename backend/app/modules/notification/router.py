from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.notification import service, schemas
from app.modules.notification.models import NotificationPreference
from app.core.security import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/me", response_model=list[schemas.NotificationOut])
def my_notifications(unread_only: bool = False, db=Depends(get_db), current_user=Depends(get_current_user)):
    return service.list_notifications(db, current_user.id, unread_only)

@router.post("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(notification_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return service.mark_read(db, notification_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/preferences", response_model=list[schemas.NotificationPreferenceOut])
def get_preferences(db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(NotificationPreference).filter_by(user_id=current_user.id).all()

@router.put("/preferences", response_model=schemas.NotificationPreferenceOut)
def update_preference(data: schemas.NotificationPreferenceUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return service.upsert_preference(db, current_user.id, data.channel, data.enabled)
