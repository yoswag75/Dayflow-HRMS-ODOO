from sqlalchemy.orm import Session
from app.modules.notification.models import Notification, NotificationPreference, NotificationChannel
from app.modules.notification.schemas import NotificationCreate, NotificationOut
from app.modules.notification.providers import get_email_provider

def create_notification(db: Session, data: NotificationCreate) -> NotificationOut:
    notif = Notification(**data.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    _maybe_dispatch_email(db, notif)
    return NotificationOut.model_validate(notif)

def _maybe_dispatch_email(db: Session, notif: Notification):
    pref = db.query(NotificationPreference).filter_by(
        user_id=notif.user_id, channel=NotificationChannel.EMAIL, enabled=True
    ).first()
    if pref:
        import asyncio
        provider = get_email_provider()
        asyncio.create_task(provider.send(
            to=_get_user_email(db, notif.user_id),
            subject=notif.title,
            body=notif.body
        ))

def mark_read(db: Session, notification_id: int, user_id: int) -> NotificationOut:
    notif = db.query(Notification).filter_by(id=notification_id, user_id=user_id).first()
    if not notif:
        raise ValueError("Notification not found or access denied")
    notif.read = True
    db.commit()
    db.refresh(notif)
    return NotificationOut.model_validate(notif)

def list_notifications(db: Session, user_id: int, unread_only: bool = False) -> list[NotificationOut]:
    q = db.query(Notification).filter_by(user_id=user_id)
    if unread_only:
        q = q.filter_by(read=False)
    return [NotificationOut.model_validate(n) for n in q.order_by(Notification.created_at.desc()).all()]

def upsert_preference(db: Session, user_id: int, channel, enabled: bool) -> NotificationPreference:
    pref = db.query(NotificationPreference).filter_by(user_id=user_id, channel=channel).first()
    if pref:
        pref.enabled = enabled
    else:
        pref = NotificationPreference(user_id=user_id, channel=channel, enabled=enabled)
        db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref

def _get_user_email(db: Session, user_id: int) -> str:
    try:
        from app.modules.auth.models import User
        user = db.query(User).filter_by(id=user_id).first()
        return user.email if user else ""
    except ImportError:
        return ""
