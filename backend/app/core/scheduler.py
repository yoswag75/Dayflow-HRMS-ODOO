from apscheduler.schedulers.background import BackgroundScheduler
from app.shared.change_request.service import run_due_change_requests


def trigger_due_change_requests(db=None):
    if db is None:
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            run_due_change_requests(db)
        finally:
            db.close()
    else:
        run_due_change_requests(db)


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(trigger_due_change_requests, "cron", hour=0, minute=5)
    scheduler.start()
    return scheduler
