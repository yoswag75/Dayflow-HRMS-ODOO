from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    session_id: int
    message: str

class ChatSessionOut(BaseModel):
    id: int
    employee_id: int
    started_at: datetime
    model_config = {"from_attributes": True}

class ChatMessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}
