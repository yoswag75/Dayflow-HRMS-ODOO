from sqlalchemy import Column, Integer, String, Date, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ChangeRequest(Base):
    __tablename__ = "change_requests"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(64), nullable=False)
    entity_id = Column(Integer, nullable=False)
    payload = Column(JSON, nullable=False)
    effective_date = Column(Date, nullable=False)
    status = Column(String(16), default="PENDING", nullable=False)  # PENDING/APPLIED/FAILED/CANCELLED
    requested_by = Column(Integer, nullable=False)
    approved_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_at = Column(DateTime(timezone=True), nullable=True)
