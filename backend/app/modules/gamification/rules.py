from dataclasses import dataclass
from typing import Optional

@dataclass
class PointRule:
    name: str
    points: int
    badge_threshold: Optional[int] = None
    badge_name: Optional[str] = None

ATTENDANCE_STREAK_RULES: list[PointRule] = [
    PointRule("STREAK_3",  points=10,  badge_threshold=3,  badge_name="On a Roll"),
    PointRule("STREAK_7",  points=25,  badge_threshold=7,  badge_name="Week Warrior"),
    PointRule("STREAK_30", points=100, badge_threshold=30, badge_name="Iron Attendance"),
]

def evaluate_streak_points(streak_days: int) -> list[PointRule]:
    """Returns rules that trigger for this streak. Pure function."""
    return [r for r in ATTENDANCE_STREAK_RULES if r.badge_threshold and streak_days >= r.badge_threshold]

def calculate_daily_checkin_points() -> int:
    return 5

def evaluate_badge_from_ledger(total_points: int, badge_criteria: dict) -> bool:
    """Generic ledger-total badge unlock check."""
    if badge_criteria.get("type") == "total_points":
        return total_points >= badge_criteria["threshold"]
    return False
