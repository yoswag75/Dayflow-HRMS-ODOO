from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint, func, Index
from app.core.database import Base

class PointsLedger(Base):
    __tablename__ = "points_ledger"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    points = Column(Integer, nullable=False)
    reason = Column(String(255))           # "ATTENDANCE_STREAK_7", "BADGE_AWARDED"
    source_module = Column(String(50))     # "attendance", "leave", "system"
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_points_ledger_employee_created", "employee_id", "created_at"),
    )

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    icon = Column(String(255))             # emoji or URL
    criteria_json = Column(JSON)           # {"type": "streak", "threshold": 7}

class EmployeeBadge(Base):
    __tablename__ = "employee_badges"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("employee_id", "badge_id"),)
