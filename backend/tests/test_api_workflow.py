from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


def test_admin_to_employee_workflow():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    try:
        setup = client.post("/auth/setup", json={"email": "admin@example.com", "password": "AdminPassword123!"})
        assert setup.status_code == 201, setup.text
        admin_headers = {"Authorization": f"Bearer {setup.json()['access_token']}"}

        onboard = client.post("/employees", headers=admin_headers, json={
            "first_name": "Test",
            "last_name": "Employee",
            "email": "employee@example.com",
            "designation": "Engineer",
            "department": "Engineering",
            "date_of_joining": "2026-08-22",
        })
        assert onboard.status_code == 201
        employee = onboard.json()["employee"]
        temporary_password = onboard.json()["temp_password"]

        login = client.post("/auth/login", json={"email": "employee@example.com", "password": temporary_password})
        assert login.status_code == 200
        employee_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        changed = client.post("/auth/change-password", headers=employee_headers, json={"password": "EmployeePassword123!"})
        assert changed.status_code == 200
        employee_headers = {"Authorization": f"Bearer {changed.json()['access_token']}"}

        assert client.get(f"/employees/{employee['id']}", headers=employee_headers).status_code == 200
        assert client.post("/attendance/check-in", headers=employee_headers).status_code == 201
        assert client.post("/attendance/check-out", headers=employee_headers).status_code == 200

        leave = client.post("/leave/apply", headers=employee_headers, json={
            "employee_id": employee["id"],
            "leave_type": "PAID",
            "start_date": "2026-09-01",
            "end_date": "2026-09-02",
            "reason": "Personal leave",
        })
        assert leave.status_code == 201
        assert client.get("/leave/me", headers=employee_headers).json()[0]["status"] == "PENDING"
        assert client.post(f"/leave/{leave.json()['id']}/approve", headers=admin_headers).status_code == 200

        tasks = client.get("/onboarding/me", headers=employee_headers)
        assert tasks.status_code == 200
        assert len(tasks.json()) > 0
        assert client.patch(f"/onboarding/tasks/{tasks.json()[0]['id']}", headers=employee_headers).status_code == 200
    finally:
        app.dependency_overrides.clear()
