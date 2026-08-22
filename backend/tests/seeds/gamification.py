from app.modules.gamification.models import Badge

def seed_badges(db):
    badges = [
        Badge(name="On a Roll",       description="3-day attendance streak",  icon="🔥", criteria_json={"type": "streak", "threshold": 3}),
        Badge(name="Week Warrior",    description="7-day attendance streak",  icon="⚡", criteria_json={"type": "streak", "threshold": 7}),
        Badge(name="Iron Attendance", description="30-day attendance streak", icon="🏆", criteria_json={"type": "streak", "threshold": 30}),
        Badge(name="Point Collector", description="Earned 500 total points",  icon="💎", criteria_json={"type": "total_points", "threshold": 500}),
    ]
    db.add_all(badges)
    db.commit()
