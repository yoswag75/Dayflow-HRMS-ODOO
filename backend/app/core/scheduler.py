import asyncio
from typing import Callable

# A simple scheduler for Dayflow HRMS
class Scheduler:
    def __init__(self):
        self.jobs = []

    def scheduled_job(self, trigger: str, hour: int):
        def decorator(func: Callable):
            self.jobs.append({
                "trigger": trigger,
                "hour": hour,
                "func": func
            })
            return func
        return decorator

scheduler = Scheduler()

@scheduler.scheduled_job("cron", hour=1)  # runs at 1 AM daily
def run_daily_gamification():
    from app.core.database import SessionLocal
    from app.modules.gamification.service import evaluate_attendance_streak, evaluate_badge_criteria
    from app.modules.employee.service import get_all_active_employees
    
    with SessionLocal() as db:
        try:
            # Note: get_all_active_employees needs to be implemented by Dev A
            employees = get_all_active_employees(db)
            for emp in employees:
                evaluate_attendance_streak(db, emp.id)
                evaluate_badge_criteria(db, emp.id)
        except Exception as e:
            print(f"Error running daily gamification job: {e}")
