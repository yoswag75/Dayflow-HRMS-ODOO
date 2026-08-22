
### Task 1 — `core/security.py`

**Files:**
- Write: `backend/app/core/security.py`
- Write: `backend/tests/test_security.py`

- [ ] Write the failing tests

```python
# backend/tests/test_security.py
from app.core.security import hash_password, verify_password, create_access_token, decode_token

def test_hash_and_verify():
    h = hash_password("secret")
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)

def test_access_token_roundtrip():
    token = create_access_token({"sub": "1", "role": "EMPLOYEE"})
    data = decode_token(token)
    assert data["sub"] == "1"
    assert data["role"] == "EMPLOYEE"

def test_expired_token_raises():
    import pytest
    token = create_access_token({"sub": "1"}, expires_minutes=-1)
    with pytest.raises(Exception):
        decode_token(token)

- [ ] Run — expect ImportError/FAIL
- [ ] Implement

# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError

SECRET_KEY = "dev-secret-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")

- [ ] Run tests — expect PASS
- [ ] git add backend/app/core/security.py backend/tests/test_security.py && git commit -m "feat: core security primitives (hash, JWT)"

---

Task 2 — modules/auth models + schemas

Files:
- Write: backend/app/modules/auth/models.py (replace stub)
- Write: backend/app/modules/auth/schemas.py
- Write: backend/tests/test_auth_models.py
- [ ] Write failing test

# backend/tests/test_auth_models.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.auth.models import User, Role

def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_sam
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_create_user():
it(); db.refresh(u)
    assert u.id is not None
    assert u.role == Role.EMPLOYEE

- [ ] Run — expect FAIL
- [ ] Implement

# backend/app/modules/auth/models.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    HR = "HR"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True)
    force_password_change = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# backend/app/modules/auth/schemas.py
from pydantic import BaseModel, EmailStr
from app.modules.auth.models import Role

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    role: Role
    employee_id: int | None = None

    model_config = {"from_attributes": True}

- [ ] Run tests — expect PASS
- [ ] git commit -m "feat: auth models (User, Role) and schemas"

---

Task 3 — modules/auth service + router + get_current_user

Files:
- Write: backend/app/modules/auth/service.py
- Write: backend/app/modules/auth/router.py
- Modify: backend/app/core/security.py (add get_current_user dependency)
- Write: backend/tests/test_auth_service.py
- [ ] Write failing tests

# backend/tests/test_auth_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.auth.models import User, Role
from app.modules.auth.service import authenticate_user, create_user
from app.core.security import hash_password

te_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_authenticate_user_success():
    db = make_db()
    db.add(User(email="x@y.com", hashed_password=hash_password("pass"), role=Role.EMPLOYEE, is_active=True))
    db.commit()
    user = authenticate_user(db, "x@y.com", "pass")
    assert user is not None
    assert user.email == "x@y.com"

def test_authenticate_user_wrong_password():
    db = make_db()
    db.add(User(email="x@y.com", hashed_password=hash_password("pass"), role=Role.EMPLOYEE, is_active=True))
    db.commit()
    assert authenticate_user(db, "x@y.com", "wrong") is None

def test_authenticate_user_not_found():
    db = make_db()
    assert authenticate_user(db, "no@one.com", "pass") is None

- [ ] Run — expect FAIL
- [ ] Implement service

# backend/app/modules/auth/service.py
from sqlalchemy.orm import Session
from app.modules.auth.models import User, Role
from app.modules.auth.schemas import TokenPair, UserOut
from app.core.security import verify_password, hash_password, create_access_token

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, email: str, password: str, role: Role = Role.EMPLOYEE) -> User:
    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return user

def issue_tokens(user: User) -> TokenPair:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenPair(access_token=token)

- [ ] Add get_current_user to core/security.py

# append to backend/app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.modules.auth.models import User  # late import to avoid circular
    try:
        data = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(data["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

- [ ] Implement router

# backend/app/modules/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.schemas import LoginRequest, TokenPair, UserOut
from app.modules.auth.service import authenticate_user, issue_tokens

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenPair)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return issue_tokens(user)

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

- [ ] Wire into main.py — add to imports and app.include_router(auth_rout
- [ ] Run tests — expect PASS
- [ ] git commit -m "feat: auth service, router, get_current_user dependency"

---

Task 4 — shared/change_request

Files:
- Write: backend/app/shared/change_request/models.py
- Write: backend/app/shared/change_request/schemas.py
- Write: backend/app/shared/change_request/service.py
- Write: backend/tests/test_change_request.py
- [ ] Write failing tests

# backend/tests/test_change_request.py
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.shared.change_request.schemas import ChangeRequestCreate
from app.shared.change_request.service import (
    create_change_request, get_due_change_requests,
    register_applier, run_due_change_requests
)

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_create_change_request():
    db = make_db()
    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=1,
        payload={"field": "value"},
        effective_date=date.today()
    )
    cr = create_change_request(db, data, requested_by=1)
    assert cr.id is not None
    assert cr.status == "PENDING"

def test_run_due_applies_pending():
    db = make_db()
    applied = []

    def fake_applier(db, cr):
        applied.append(cr.entity_id)

    register_applier("test_entity", fake_applier)

    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=42,
        payload={"x": 1},
        effective_date=date.today()
    )
    create_change_request(db, data, requested_by=1)
    run_due_change_requests(db)

    assert 42 in applied

def test_future_cr_not_applied():
    db = make_db()
    applied = []
    register_applier("test_entity", lambda db, cr: applied.append(cr.id))

    data = ChangeRequestCreate(
        entity_type="test_entity",
        entity_id=99,
        payload={},
        effective_date=date.today() + timedelta(days=30)
    )
    create_change_request(db, data, requested_by=1)
    run_due_change_requests(db)
    assert applied == []

- [ ] Run — expect FAIL
- [ ] Implement models

# backend/app/shared/change_request/models.py
from sqlalchemy import Column, Integer, String, Date, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class ChangeRequest(Base):
    __tablename__ = "change_requests"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(64), nullable=False)
    entity_id = Column(Integer, nullable=False)
    payload = Column(JSON, nullable=False)
    effective_date = Column(Date, nullable=False)
    status = Column(String(16), default="PENDING", nullable=False)  # PENDING/APPLIED/FAILED/CANCELLED
    requested_by = Column(Integer, nullable=False)
    approved_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_at = Column(DateTime(timezone=True), nullable=True)

- [ ] Implement schemas

# backend/app/shared/change_request/schemas.py
from datetime import date, datetime
from pydantic import BaseModel

class ChangeRequestCreate(BaseModel):
    entity_type: str
    entity_id: int
    payload: dict
    effective_date: date

class ChangeRequestOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    payload: dict
    effective_date: date
    status: str
    requested_by: int
    approved_by: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

- [ ] Implement service

# backend/app/shared/change_request/service.py
from datetime import date, datetime, timezone
from typing import Callable
from sqlalchemy.orm import Session
from app.shared.change_request.models import ChangeRequest
from app.shared.change_request.schemas import ChangeRequestCreate, ChangeRequestOut

APPLIER_REGISTRY: dict[str, Callable] = {}

def register_applier(entity_type: str, fn: Callable) -> None:
    APPLIER_REGISTRY[entity_type] = fn

def create_change_request(db: Session, data: ChangeRequestCreate, requested_by: int) -> ChangeRequestOut:
    cr = ChangeRequest(**data.model_dump(), requested_by=requested_by)
    db.add(cr); db.commit(); db.refresh(cr)
    return ChangeRequestOut.model_validate(cr)

def get_due_change_requests(db: Session, as_of: date | None = None) -> list[ChangeRequestOut]:
    as_of = as_of or date.today()
    rows = db.query(ChangeRequest).filter(
        ChangeRequest.status == "PENDING",
        ChangeRequest.effective_date <= as_of
    ).all()
    return [ChangeRequestOut.model_validate(r) for r in rows]

def run_due_change_requests(db: Session, as_of: date | None = None) -> None:
    for cr in get_due_change_requests(db, as_of):
        applier = APPLIER_REGISTRY.get(cr.entity_type)
        row = db.query(ChangeRequest).get(cr.id)
        try:
            if applier:
                applier(db, cr)
            row.status = "APPLIED"
            row.applied_at = datetime.now(timezone.utc)
        except Exception:
            row.status = "FAILED"
        db.commit()

- [ ] Run tests — expect PASS
- [ ] git commit -m "feat: shared change_request engine with applier registry"

---

Task 5 — modules/employee

Files:
- Create: backend/app/modules/employee/models.py
- Create: backend/app/modules/employee/schemas.py
- Create: backend/app/modules/employee/service.py

**Files:**
- Create: `backend/app/modules/employee/models.py`
- Create: `backend/app/modules/employee/schemas.py`
- Create: `backend/app/modules/employee/service.py`
- Create: `backend/app/modules/employee/router.py`
- Write: `backend/tests/test_employee.py`

- [ ] Write failing tests

```python
# backend/tests/test_employee.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.employee.schemas import EmployeeCreate
from app.modules.employee.service import create_employee, get_employee_by_id, list_employees

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_create_and_fetch_employee():
    db = make_db()
    data = EmployeeCreate(
mp.id is not None
    fetched = get_employee_by_id(db, emp.id)
    assert fetched.email == "ada@dayflow.hr"

def test_list_employees():
    db = make_db()
    for i in range(3):
        create_employee(db, EmployeeCreate(
            first_name=f"User{i}", last_name="Test",
            email=f"u{i}@dayflow.hr", designation="Analyst",
            department="HR", date_of_joining="2024-01-01"
        ))
et_employee_by_id(db, 9999) is None

- [ ] Run — expect FAIL
- [ ] Implement models

# backend/app/modules/employee/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from app.core.database import Base
import enum

class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
joining = Column(Date)
    salary_band = Column(String(50), nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE)

- [ ] Implement schemas

# backend/app/modules/employee/schemas.py
from datetime import date
from pydantic import BaseModel, EmailStr
from app.modules.employee.models import EmployeeStatus

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    designation: str | None = None
    department: str | None = None
    date_of_joining: date | None = None
    salary_band: str | None = None
    manager_id: int | None = None

class EmployeeUpdate(BaseModel):
    designation: str | None = None
    department: str | None = None
band: str | None
    manager_id: int | None
    status: EmployeeStatus

    model_config = {"from_attributes": True}

- [ ] Implement service

# backend/app/modules/employee/service.py
from datetime import date
from sqlalchemy.orm import Session
from app.modules.employee.models import Employee
from app.modules.employee.schemas import EmployeeCreate, EmployeeOut
EmployeeOut.model_validate(emp) if emp else None

def list_employees(db: Session, department: str | None = None) -> list[EmployeeOut]:
    q = db.query(Employee)
    if department:
        q = q.filter(Employee.department == department)
    return [EmployeeOut.model_validate(e) for e in q.all()]

def request_employee_change(db: Session, employee_id: int, payload: dict,
                             effective_date: date, requested_by: int):
    return create_change_request(db, ChangeRequestCreate(
        entity_type="employee",
it()

register_applier("employee", _apply_employee_change)

- [ ] Implement router

# backend/app/modules/employee/router.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.employee.schemas import EmployeeCreate, EmployeeOut
from app.modules.employee.service import create_employee, get_employee_by_id, list_employees, request_employee_change

router = APIRouter(prefix="/employees", tags=["Employee"])
(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    emp = get_employee_by_id(db, id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.post("/{id}/change-requests", status_code=201)
router into main.py
- [ ] Run tests — expect PASS
- [ ] git commit -m "feat: employee module — CRUD + change request integration"

---

SPRINT 2

---

dules/attendance

Files:
- Create: backend/app/modules/attendance/models.py
- Create: backend/app/modules/attendance/schemas.py
- Create: backend/app/modules/attendance/service.py
- Create: backend/app/modules/attendance/router.py
- Write: backend/tests/test_attendance.py
- [ ] Write failing tests

# backend/tests/test_attendance.py
from datetime import date, datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_clock_in_creates_record():
    db = make_db()
    record = clock_in(db, employee_id=1)
    assert record.id is not None
    assert record.check_in is not None
    assert record.check_out is None

def test_clock_out_sets_time():
    db = make_db()
    clock_in(db, employee_id=1)
    record = clock_out(db, employee_id=1)
    assert record.check_out is not None

def test_double_clock_in_raises():
    import pytest
    db = make_db()
    clock_in(db, employee_id=1)
    with pytest.raises(ValueError, match="already checked in"):
        clock_in(db, employee_id=1)
db, employee_id=1)
    records = get_attendance_for_period(db, employee_id=1,
                                        start=date.today(), end=date.today())
    assert len(records) == 1

- [ ] Run — expect FAIL
- [ ] Implement models

# backend/app/modules/attendance/models.py
import enum
from sqlalchemy import Column, Integer, Date, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    ON_LEAVE = "ON_LEAVE"

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
 Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)

- [ ] Implement schemas

# backend/app/modules/attendance/schemas.py
from datetime import date, datetime
from pydantic import BaseModel
from app.modules.attendance.models import AttendanceStatus

class AttendanceRecordOut(BaseModel):
    id: int
d: int
    date: date
    check_in: datetime | None
    check_out: datetime | None
    status: AttendanceStatus

    model_config = {"from_attributes": True}

- [ ] Implement service

# backend/app/modules/attendance/service.py
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.attendance.schemas import AttendanceRecordOut

def clock_in(db: Session, employee_id: int) -> AttendanceRecordOut:
    today = date.today()
    existing = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date == today,
        AttendanceRecord.check_out == None
    ).first()
    if existing:
        raise ValueError("Employee already checked in today")
    record = AttendanceRecord(
        employee_id=employee_id,
        date=today,
        check_in=datetime.now(timezone.utc),
        status=AttendanceStatus.PRESENT
    )
    db.add(record); db.commit(); db.refresh(record)
    return AttendanceRecordOut.model_validate(record)

def clock_out(db: Session, employee_id: int) -> AttendanceRecordOut:
    today = date.today()
    record = db.query(AttendanceRecord).filter(
anceRecord.date == today,
        AttendanceRecord.check_out == None
    ).first()
    if not record:
        raise ValueError("No active check-in found")
    record.check_out = datetime.now(timezone.utc)
    db.commit(); db.refresh(record)
    return AttendanceRecordOut.model_validate(record)

def get_attendance_for_period(db: Session, employee_id: int,
                               start: date, end: date) -> list[AttendanceRecordOut]:
    rows = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date >= start,
        AttendanceRecord.date <= end
    ).all()
    return [AttendanceRecordOut.model_validate(r) for r in rows]

def get_attendance_summary(db: Session, employee_id: int, month: int, year: int) -> dict:
    from datetime import date as d
    import calendar
    start = d(year, month, 1)
    end = d(year, month, calendar.monthrange(year, month)[1])
    records = get_attendance_for_period(db, employee_id, start, end)
    return {
        "present": sum(1 for r in records if r.status == AttendanceStatus.PRESENT),
        "absent": sum(1 for r in records if r.status == AttendanceStatus.ABSENT),
        "total_days": len(records)
    }

- [ ] Implement router + wire into main.py

# backend/app/modules/attendance/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/clock-in", response_model=AttendanceRecordOut, status_code=201)
def do_clock_in(db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return clock_in(db, employee_id=user.employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/clock-out", response_model=AttendanceRecordOut)
def do_clock_out(db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
ueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=list[AttendanceRecordOut])
def my_attendance(start: date, end: date, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_attendance_for_period(db, user.employee_id, start, end)

- [ ] Run tests — expect PASS
- [ ] git commit -m "feat: attendance module — clock-in/out, period query

---

Task 7 — modules/onboarding

Files:
- Create: backend/app/modules/onboarding/models.py
- Create: backend/app/modules/onboarding/schemas.py
- Create: backend/app/modules/onboarding/service.py
- Create: backend/app/modules/onboarding/router.py
- Write: backend/tests/test_onboarding.py
- [ ] Write failing tests

# backend/tests/test_onboarding.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.onboarding.service import create_checklist, complete_tas

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_create_checklist():
    db = make_db()
    tasks = create_checklist(db, employee_id=1, role="Engineer")
    assert len(tasks) > 0
    assert all(t.status == "PENDING" for t in tasks)

def test_complete_task():
()
    tasks = create_checklist(db, employee_id=1, role="Engineer")
    updated = complete_task(db, task_id=tasks[0].id)
    assert updated.status == "DONE"

def test_get_status():
    db = make_db()
    tasks = create_checklist(db, employee_id=1, role="Engineer")
    complete_task(db, task_id=tasks[0].id)
    status = get_status(db, employee_id=1)
    assert status["completed"] == 1
    assert status["total"] == len(tasks)

- [ ] Run — expect FAIL
- [ ] Implement models

# backend/app/modules/onboarding/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.core.database import Base

class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    task_name = Column(String(200), nullable=False)
    status = Column(String(16), default="PENDING")  # PENDING / DONE
    due_date = Column(Date, nullable=True)
rt date
from pydantic import BaseModel

class OnboardingTaskOut(BaseModel):
    id: int
    employee_id: int
    task_name: str
    status: str
    due_date: date | None
    model_config = {"from_attributes": True}

# backend/app/modules/onboarding/service.py
from sqlalchemy.orm import Session
from app.modules.onboarding.models import OnboardingTask
from app.modules.onboarding.schemas import OnboardingTaskOut
Setup laptop", "Read codebase docs", "Meet your buddy", "Complete HR forms"],
    "HR": ["Read HR policy", "Setup accounts", "Meet your buddy", "Complete HR forms"],
    "default": ["Setup accounts", "Meet your buddy", "Complete HR forms"],
}

def create_checklist(db: Session, employee_id: int, role: str) -> list[OnboardingTaskOut]:
    tasks_names = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["default"])
    tasks = [OnboardingTask(employee_id=employee_id, task_name=name, role_template=role)
             for name in tasks_names]
    db.add_all(tasks); db.commit()
    for t in tasks: db.refresh(t)
    return [OnboardingTaskOut.model_validate(t) for t in tasks]

def complete_task(db: Session, task_id: int) -> OnboardingTaskOut:
    task = db.query(OnboardingTask).filter(OnboardingTask.id == task_id).first()
    if not task:
        raise ValueError("Task not found")
    task.status = "DONE"
    db.commit(); db.refresh(task)
    return OnboardingTaskOut.model_validate(task)

def get_status(db: Session, employee_id: int) -> dict:
    tasks = db.query(OnboardingTask).filter(OnboardingTask.employee_id == employee_id).all()
    done = sum(1 for t in tasks if t.status == "DONE")
    return {"total": len(tasks), "completed": done, "remaining": len(tasks) - done}


---

Task 8 — modules/leave

Files:
- Create: backend/app/modules/leave/models.py
- Create: backend/app/modules/leave/schemas.py
- Create: backend/app/modules/leave/service.py
- Create: backend/app/modules/leave/router.py
- Write: backend/tests/test_leave.py
- [ ] Write failing tests

# backend/tests/test_leave.py
import pytest
from sqlalchemy import create_engine

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_apply_leave_creates_pending():
    db = make_db()
    seed_balances(db, employee_id=1)
    req = LeaveRequestCreate(employee_id=1, leave_type="PAID", start_date="2026-09-01", end_date="2026-09-03", reason="Holiday")
    result = apply_leave(db, req)
    assert result.status == "PENDING"

def test_approve_leave_deducts_balance():
    db = make_db()
stCreate(employee_id=1, leave_type="PAID", start_date="2026-09-01", end_date="2026-09-03", reason="Holiday")
    leave = apply_leave(db, req)
    approve_leave(db, leave_id=leave.id, approver_id=99)
    balance = get_leave_balance(db, employee_id=1)
    paid = next(b for b in balance if b.leave_type == "PAID")
    assert paid.balance == 17  # 20 - 3 days

def test_insufficient_balance_raises():
    db = make_db()
    seed_balances(db, employee_id=1, paid_quota=1)
    req = LeaveRequestCreate(employee_id=1, leave_type="PAID", start_date-09-05", reason="Holiday")
    leave = apply_leave(db, req)
    with pytest.raises(ValueError, match="Insufficient"):
        approve_leave(db, leave_id=leave.id, approver_id=99)

- [ ] Run — expect FAIL
- [ ] Implement models

# backend/app/modules/leave/models.py
import enum
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from app.core.database import Base

class LeaveType(str, enum.Enum):
    PAID = "PAID"
    SICK = "SICK"
    UNPAID = "UNPAID"
    EMERGENCY = "EMERGENCY"

class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    id = Column(Integer, primary_key=True)
nteger, nullable=True)

- [ ] Implement schemas + service

# backend/app/modules/leave/schemas.py
from datetime import date
from pydantic import BaseModel

class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None = None

class LeaveRequestOut(BaseModel):
    id: int

    balance: int
    model_config = {"from_attributes": True}

# backend/app/modules/leave/service.py
from sqlalchemy.orm import Session
from app.modules.leave.models import LeaveBalance, LeaveRequest
from app.modules.leave.schemas import LeaveRequestCreate, LeaveRequestOut, LeaveBalanceOut

DEFAULT_QUOTAS = {"PAID": 20, "SICK": 10, "UNPAID": 30, "EMERGENCY": 3}

def seed_balances(db: Session, employee_id: int, paid_quota: int = 20) -> None:
    quotas = {**DEFAULT_QUOTAS, "PAID": paid_quota}
    for leave_type, quota in quotas.items():
        db.add(LeaveBalance(employee_id=employee_id, leave_type=leave_type, balance=quota))
    db.commit()

        raise ValueError("Leave request not found")
    days = (req.end_date - req.start_date).days + 1
    balance = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == req.employee_id,
        LeaveBalance.leave_type == req.leave_type
    ).first()
    if balance and req.leave_type != "UNPAID":
        if balance.balance < days:
            raise ValueError(f"Insufficient {req.leave_type} balance")
        balance.balance -= days
.model_validate(req)

def get_leave_balance(db: Session, employee_id: int) -> list[LeaveBalanceOut]:
    rows = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).all()
    return [LeaveBalanceOut.model_validate(r) for r in rows]

- [ ] Wire router + add to main.py
- [ ] Run tests — expect PASS
- [ ] git commit -m "feat: leave module — apply, approve, balance tracking"

---

SPRINT 4

---

Task 9 — modules/payroll

Files:
- Create: backend/app/modules/payroll/models.py
- Create: backend/app/modules/payroll/schemas.py
- Create: backend/app/modules/payroll/calculators.py
- Create: backend/app/modules/payroll/service.py
- Create: backend/app/modules/payroll/router.py
- Write: backend/tests/test_payroll_calculators.py
- Write: backend/tests/test_payroll_service.py
- [ ] Write calculator tests (no DB needed)

# backend/tests/test_payroll_calculators.py

        unpaid_absent_days=1
    )
    assert deductions["unpaid_leave"] == Decimal("2000")

def test_calculate_net():
    net = calculate_net(gross=Decimal("75000"), deductions={"unpaid_leave": Decimal("2000")})
    assert net == Decimal("73000")

- [ ] Run — expect FAIL
- [ ] Implement calculators

# backend/app/modules/payroll/calculators.py
from decimal import Decimal

def calculate_gross(basic: int, hra: int, allowances: dict) -> Decimal:
    return Decimal(basic) + Decimal(hra) + sum(Decimal(v) for v in allowances.values())

ce.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.payroll.models import SalaryStructure
from app.modules.payroll.service import run_payroll, request_salary_change
from app.modules.employee.models import Employee
from app.modules.attendance.models import AttendanceRecord
from datetime import date

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_salary_change_request_creates_cr():
    db = make_db()
    cr = request_salary_change(db, employee_id=1,
                                payload={"basic": 60000},
                                effective_date=date(2026, 9, 1),
                                requested_by=99)
    assert cr.entity_type == "salary_structure"
    assert cr.status == "PENDING"

eger, String, Date, DateTime, JSON, Numeric, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False)
    basic = Column(Integer, nullable=False)
    hra = Column(Integer, default=0)
    allowances_json = Column(JSON, default={})
    effective_date = Column(Date, nullable=True)

class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    id = Column(Integer, primary_key=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(16), default="DRAFT")  # DRAFT/PROCESSED/PAID
    processed_at = Column(DateTime(timezone=True), nullable=True)

class Payslip(Base):
    __tablename__ = "payslips"
    id = Column(Integer, primary_key=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=Fa

class PayslipOut(BaseModel):
    id: int
    employee_id: int
    gross: Decimal
    deductions_json: dict
    net_pay: Decimal
    generated_at: datetime
    model_config = {"from_attributes": True}

class PayrollRunOut(BaseModel):
    id: int
    month: int
    year: int
    status: str
    payslips: list[PayslipOut] = []
    model_config = {"from_attributes": True}

- [ ] Implement service
 year: int) -> PayrollRunOut:
    run = PayrollRun(month=month, year=year, status="DRAFT")
    db.add(run); db.commit(); db.refresh(run)

    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    working_days = (end - start).days + 1
    payslips = []

    employees = db.query(Employee).filter(Employee.status == EmployeeStat

            payroll_run_id=run.id, employee_id=emp.id,
            gross=gross, deductions_json=deductions, net_pay=net
        )
        db.add(slip)
        payslips.append(slip)

    run.status = "PROCESSED"
    run.processed_at = datetime.now(timezone.utc)
    db.commit()
un)
    out.payslips = [PayslipOut.model_validate(s) for s in payslips]
    return out

def request_salary_change(db: Session, employee_id: int, payload: dict,
                           effective_date: date, requested_by: int):
    return create_change_request(db, ChangeRequestCreate(
        entity_type="salary_structure",
        entity_id=employee_id,
        payload=payload,
        effective_date=effective_date
    ), requested_by=requested_by)

def _apply_salary_change(db: Session, cr) -> None:
    salary = db.query(SalaryStructure).filter(SalaryStructure.employee_id == cr.entity_id).first()
    if not salary:
        raise ValueError(f"SalaryStructure for employee {cr.entity_id} no
    for field, value in cr.payload.items():
        setattr(salary, field, value)
    db.commit()

register_applier("salary_structure", _apply_salary_change)

- [ ] Wire router + add to main.py
- [ ] Run all tests — expect PASS
- [ ] git commit -m "feat: payroll module — run_payroll, payslips, salary change requests"

---
e_request, register_applier
from app.core.scheduler import trigger_due_change_requests

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()

def test_scheduler_triggers_due_requests():

    trigger_due_change_requests(db)
    assert cr.id in applied

- [ ] Run — expect FAIL
- [ ] Implement

# backend/app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.shared.change_request.service import run_due_change_requests

# Import modules so their register_applier() calls fire on startup

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

- [ ] Add to main.py startup

# in main.py, add to lifespan or on_event
from app.core.scheduler import start_scheduler

@app.on_event("startup")
def startup():
    start_scheduler()


Files:
- Write: backend/tests/test_integration_payroll.py
- [ ] Write test

# backend/tests/test_integration_payroll.py
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.employee.models import Employee, EmployeeStatus
from app.modules.payroll.models import SalaryStructure
from app.modules.payroll.service import run_payroll, request_salary_chang
from app.core.scheduler import trigger_due_change_requests

def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)


    # Run payroll for August — should use basic=50000
    aug_run = run_payroll(db, month=8, year=2026)
    assert aug_run.payslips[0].gross == 50000

    # Request salary bump effective Sep 1
    request_salary_change(db, emp.id, {"basic": 70000}, date(2026, 9, 1), requested_by=1)

    # Simulate scheduler running on Sep 1
    trigger_due_change_requests(db)

    assert sep_run.payslips[0].gross == 70000

- [ ] Run — expect PASS (if all previous tasks done correctly)
- [ ] git commit -m "test: integration — salary change request → scheduler → payroll picks up new value"

---

Final Checklist

- [ ] All 11 task test suites pass: pytest backend/tests/ -v
- [ ] main.py includes routers for: auth, employee, attendance, onboarding, leave, payroll
- [ ] PayslipOut schema frozen — notify Dev B it's in backend/app/modules/payroll/schemas.py
- [ ] EmployeeOut schema frozen — notify Dev B it's in backend/app/modules/employee/schemas.py
- [ ] get_current_user import path confirmed to Dev B: from app.core.security import get_current_user

---
