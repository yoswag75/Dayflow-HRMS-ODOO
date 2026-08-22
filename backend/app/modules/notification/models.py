from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class NotificationType(str, enum.Enum):
    INFO = "INFO"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    ALERT = "ALERT"

class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(String(2000), nullable=False)
    source_module = Column(String(50), nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.INFO)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False)
    enabled = Column(Boolean, default=True)
