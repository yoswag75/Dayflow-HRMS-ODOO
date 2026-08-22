from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False)
    task_name = Column(String(200), nullable=False)
    status = Column(String(16), default="PENDING", nullable=False)  # PENDING / DONE
    due_date = Column(Date, nullable=True)
    role_template = Column(String(100), nullable=True)
