import enum
from sqlalchemy import Column, Integer, String, Date, Text
from app.core.database import Base


class LeaveType(str, enum.Enum):
    PAID = "PAID"
    SICK = "SICK"
    UNPAID = "UNPAID"
    EMERGENCY = "EMERGENCY"


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False)
    leave_type = Column(String(20), nullable=False)
    balance = Column(Integer, nullable=False)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False)
    leave_type = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(16), default="PENDING", nullable=False)  # PENDING/APPROVED/REJECTED
    reason = Column(Text, nullable=True)
    resolved_by = Column(Integer, nullable=True)
