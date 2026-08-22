from sqlalchemy import func
from sqlalchemy.orm import Session
from app.modules.gamification import rules
from app.modules.gamification.models import PointsLedger, Badge, EmployeeBadge
from app.modules.gamification.schemas import LeaderboardEntryOut, PointsLedgerOut

def award_points(db: Session, employee_id: int, points: int, reason: str, source_module: str) -> PointsLedger:
    entry = PointsLedger(employee_id=employee_id, points=points, reason=reason, source_module=source_module)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_total_points(db: Session, employee_id: int) -> int:
    result = db.query(func.sum(PointsLedger.points)).filter_by(employee_id=employee_id).scalar()
    return result or 0

def evaluate_attendance_streak(db: Session, employee_id: int) -> None:
    # SPRINT 1: Use stub
    from tests.stubs.schemas import AttendanceSummaryOut
    summary = AttendanceSummaryOut(employee_id=employee_id, total_present=0, total_absent=0, streak_days=7)

    # SPRINT 2: Swap to real (remove stub above, uncomment below):
    # from app.modules.attendance.service import get_attendance_summary
    # summary = get_attendance_summary(db, employee_id)

    for rule in rules.evaluate_streak_points(summary.streak_days):
        award_points(db, employee_id, rule.points, rule.name, "attendance")
        if rule.badge_name:
            _try_award_badge(db, employee_id, rule.badge_name)

def _try_award_badge(db: Session, employee_id: int, badge_name: str) -> None:
    badge = db.query(Badge).filter_by(name=badge_name).first()
    if not badge:
        return
    existing = db.query(EmployeeBadge).filter_by(employee_id=employee_id, badge_id=badge.id).first()
    if not existing:
        db.add(EmployeeBadge(employee_id=employee_id, badge_id=badge.id))
        db.commit()
        # Fire notification
        from app.modules.notification.service import create_notification
        from app.modules.notification.schemas import NotificationCreate
        create_notification(db, NotificationCreate(
            user_id=employee_id,
            title=f"Badge Unlocked: {badge.name}",
            body=f"You earned the '{badge.name}' badge!",
            source_module="gamification", type="INFO"
        ))

def evaluate_badge_criteria(db: Session, employee_id: int) -> None:
    total_pts = get_total_points(db, employee_id)
    for badge in db.query(Badge).all():
        if badge.criteria_json and rules.evaluate_badge_from_ledger(total_pts, badge.criteria_json):
            _try_award_badge(db, employee_id, badge.name)

def get_leaderboard(db: Session, department: str = None, period: str = "month") -> list[LeaderboardEntryOut]:
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=30 if period == "month" else 7)
    q = (db.query(PointsLedger.employee_id, func.sum(PointsLedger.points).label("total_points"))
         .filter(PointsLedger.created_at >= cutoff)
         .group_by(PointsLedger.employee_id)
         .order_by(func.sum(PointsLedger.points).desc()))
    return [
        LeaderboardEntryOut(
            rank=rank, employee_id=row.employee_id,
            employee_name=f"Employee #{row.employee_id}",  # SPRINT 2: swap for real employee name lookup
            total_points=row.total_points,
            department=department or "All"
        )
        for rank, row in enumerate(q.all(), start=1)
    ]
