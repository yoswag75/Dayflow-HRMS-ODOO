from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    INFO = "INFO"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    ALERT = "ALERT"

class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"

# PUBLIC CONTRACT — Dev A imports this line:
# from app.modules.notification.schemas import NotificationCreate
class NotificationCreate(BaseModel):
    user_id: int
    title: str
    body: str
    source_module: str
    type: NotificationType = NotificationType.INFO

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    source_module: str
    type: NotificationType
    read: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class NotificationPreferenceOut(BaseModel):
    id: int
    user_id: int
    channel: NotificationChannel
    enabled: bool
    model_config = {"from_attributes": True}

class NotificationPreferenceUpdate(BaseModel):
    channel: NotificationChannel
    enabled: bool
