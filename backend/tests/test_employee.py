from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.employee.schemas import EmployeeCreate
from app.modules.employee.service import create_employee, get_employee_by_id, list_employees, onboard_employee


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_create_and_fetch_employee():
    db = make_db()
    data = EmployeeCreate(
        first_name="Ada", last_name="Lovelace",
        email="ada@dayflow.hr", designation="Engineer",
        department="Engineering", date_of_joining="2024-01-01",
    )
    emp = create_employee(db, data)
    assert emp.id is not None
    fetched = get_employee_by_id(db, emp.id)
    assert fetched.email == "ada@dayflow.hr"


def test_list_employees():
    db = make_db()
    for i in range(3):
        create_employee(db, EmployeeCreate(
            first_name=f"User{i}", last_name="Test",
            email=f"u{i}@dayflow.hr", designation="Analyst",
            department="HR", date_of_joining="2024-01-01",
        ))
    results = list_employees(db)
    assert len(results) == 3


def test_list_employees_filter_by_department():
    db = make_db()
    create_employee(db, EmployeeCreate(
        first_name="A", last_name="B", email="a@dayflow.hr",
        designation="Dev", department="Engineering", date_of_joining="2024-01-01",
    ))
    create_employee(db, EmployeeCreate(
        first_name="C", last_name="D", email="c@dayflow.hr",
        designation="HR", department="HR", date_of_joining="2024-01-01",
    ))
    results = list_employees(db, department="Engineering")
    assert len(results) == 1
    assert results[0].department == "Engineering"


def test_get_nonexistent_employee_returns_none():
    db = make_db()
    assert get_employee_by_id(db, 9999) is None


def test_onboard_creates_linked_user():
    db = make_db()
    data = EmployeeCreate(
        first_name="Grace", last_name="Hopper",
        email="grace@dayflow.hr", designation="Engineer",
        department="Engineering", date_of_joining="2024-01-01",
    )
    emp, temp_password = onboard_employee(db, data)
    assert emp.id is not None
    assert temp_password is not None and len(temp_password) > 0
    user = db.query(User).filter(User.email == "grace@dayflow.hr").first()
    assert user is not None
    assert user.employee_id == emp.id
