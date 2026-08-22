import pytest
from unittest.mock import patch
from app.core.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modules.auth.models import User
from app.modules.gamification.models import EmployeeBadge, Badge, PointsLedger
from app.modules.notification.models import Notification
from app.modules.gamification.rules import evaluate_streak_points
from app.modules.gamification.service import award_points, get_total_points, _try_award_badge, evaluate_attendance_streak
from tests.stubs.schemas import AttendanceSummaryOut
from tests.seeds.gamification import seed_badges


# Pure unit tests — no DB fixture needed
def test_streak_rules_below_threshold():
    assert evaluate_streak_points(2) == []

def test_streak_rules_at_3():
    rules = evaluate_streak_points(3)
    assert len(rules) == 1
    assert rules[0].badge_name == "On a Roll"

def test_streak_rules_at_7():
    rules = evaluate_streak_points(7)
    assert len(rules) == 2  # On a Roll + Week Warrior

# DB-backed service tests
def test_award_points_and_retrieve(db_session):
    award_points(db_session, employee_id=1, points=25, reason="STREAK_7", source_module="attendance")
    assert get_total_points(db_session, employee_id=1) == 25

def test_badge_not_duplicated(db_session):
    seed_badges(db_session)
    _try_award_badge(db_session, employee_id=1, badge_name="On a Roll")
    _try_award_badge(db_session, employee_id=1, badge_name="On a Roll")  # second call
    count = db_session.query(EmployeeBadge).filter_by(employee_id=1).count()
    assert count == 1  # must not duplicate

def test_badge_unlocked_on_streak(db_session):
    seed_badges(db_session)
    # mock patch get_attendance_summary if it existed, but for Sprint 1 we use a stub inside the service
    # Wait, the service uses tests.stubs.schemas.AttendanceSummaryOut.
    # The patch target in the plan was "app.modules.gamification.service.get_attendance_summary"
    # For Sprint 1, the code hardcodes the stub, so we don't even need to patch it unless it calls a function.
    # We will just call evaluate_attendance_streak directly because the stub provides streak=7 in service.py
    
    evaluate_attendance_streak(db_session, employee_id=1)
    badge = db_session.query(EmployeeBadge).filter_by(employee_id=1).first()
    assert badge is not None
