**Dayflow**

**Technical Details Document**

Architecture, stack, schemas, contracts, and infrastructure

# 1. Technology Stack

| **Layer** | **Choice** | **Notes** |
| --- | --- | --- |
| Backend framework | FastAPI (Python) | Async-native; Pydantic for schema validation and inter-module contracts |
| Architecture style | Modular monolith | Single deployable app; strict per-module ownership of tables, extractable to microservices later |
| Database | PostgreSQL | One instance, one schema per module (or clearly namespaced tables) for logical separation without operational overhead |
| ORM / Migrations | SQLAlchemy + Alembic | One migration history shared across all modules |
| Auth | JWT (access token) | Issued by Auth module, verified via a shared FastAPI dependency |
| Scheduled jobs | APScheduler (in-process) | Handles change-request auto-apply, SLA escalation, absence marking, gamification tally |
| Local LLM runtime | Ollama | Hosts a small quantized open-weight model; no third-party LLM API calls |
| Candidate models | llama3.2:3b or phi3:mini | Chosen for response latency on hackathon-scale hardware; swap based on available compute |
| Inter-service HTTP client | httpx (async) | Used for Chatbot → Ollama calls |
| Containerization | Docker Compose | Services: app, postgres, ollama |

# 2. Architecture Overview

Dayflow is built as a modular monolith: a single FastAPI application internally divided into modules that mirror what would be separate microservices in a larger deployment. Each module owns its own tables and exposes a small set of service functions; no module is permitted to import or query another module's SQLAlchemy models directly. Cross-module interaction happens exclusively through the owning module's service-layer functions, using Pydantic schemas as the contract — the same shape that would be used if the call were a real HTTP request. This preserves the option to extract a module (most likely Simulation, Payroll, or Auth first) into an independent service later without a rewrite.

## 2.1 Folder Structure

/app
 main.py # mounts all module routers
 /core
 config.py # Pydantic Settings (env vars)
 database.py # SQLAlchemy engine/session, get\_db()
 security.py # JWT verification, role dependencies
 scheduler.py # APScheduler setup, registers all jobs
 /shared
 /change\_request
 models.py # ChangeRequest table
 schemas.py
 service.py # create/approve/reject/apply\_due\_changes
 /modules
 /auth (router.py, schemas.py, models.py, service.py)
 /employee (router.py, schemas.py, models.py, service.py)
 /attendance (router.py, schemas.py, models.py, service.py)
 /leave (router.py, schemas.py, models.py, service.py)
 /payroll (router.py, schemas.py, models.py, service.py)
 /gamification(router.py, schemas.py, models.py, service.py)
 /onboarding (router.py, schemas.py, models.py, service.py)
 /simulation (router.py, schemas.py, service.py) # no models.py - read-only aggregator
 /chatbot (router.py, schemas.py, service.py, ollama\_client.py)
 /notification(router.py, schemas.py, models.py, service.py)

## 2.2 Module Boundary Rule

Enforced convention: only a module's own service.py may import its own models.py. Every other module reaches its data exclusively via imported service functions, e.g.:

# modules/simulation/service.py
from app.modules.leave.service import get\_approved\_leave\_count # OK
from app.modules.attendance.service import get\_attendance\_summary # OK
# from app.modules.leave.models import LeaveRequest # NOT allowed

# 3. Database Schema (Per Module)

## 3.1 Auth

| **Table** | **Key Fields** |
| --- | --- |
| User | id, login\_id, email, password\_hash, role (admin/hr/employee), must\_change\_password, created\_at |

Login ID generation: <Company Code> + <first two letters of first name><first two letters of last name> + <year of joining> + <serial number of joining, zero-padded>. Example: 0C210C202A0001.

## 3.2 Employee

| **Table** | **Key Fields** |
| --- | --- |
| Employee | id, user\_id (FK), name, dob, doj, department, designation, manager\_id, buddy\_id, phone, address, personal\_email, marital\_status, profile\_picture\_url, about, skills (JSON), certifications (JSON), hobbies (JSON), visible\_on\_leaderboard |

* Self-serve fields (apply instantly): profile\_picture\_url, about, hobbies, skills
* Verified fields (route through Change Request): phone, address, emergency\_contact, bank\_details

## 3.3 Shared — Change Request

| **Table** | **Key Fields** |
| --- | --- |
| ChangeRequest | id, entity\_type (employee\_profile/payroll), entity\_id, field\_name, old\_value, new\_value, status (pending/approved/rejected), effective\_date (nullable), reason, requested\_by, approved\_by, created\_at, resolved\_at, is\_correction (bool) |

## 3.4 Attendance

| **Table** | **Key Fields** |
| --- | --- |
| Attendance | id, employee\_id, date, check\_in\_time, check\_out\_time, status (present/absent/half\_day/leave), work\_hours, extra\_hours, source (office/field) |

## 3.5 Leave

| **Table** | **Key Fields** |
| --- | --- |
| LeaveRequest | id, employee\_id, leave\_type (paid/sick/unpaid/emergency), start\_date, end\_date, status (pending/provisional/approved/rejected), attachment\_url, remarks, requested\_at, resolved\_at, resolved\_by, flagged (bool) |
| LeaveBalance | employee\_id, leave\_type, allocated\_days, used\_days, remaining\_days |
| EmergencyLeaveUsage | employee\_id, period, provisional\_count (for the abuse-prevention cap) |

## 3.6 Payroll

| **Table** | **Key Fields** |
| --- | --- |
| SalaryStructure | employee\_id, wage\_type (fixed/percentage), monthly\_wage, yearly\_wage, working\_days\_per\_week, base\_time\_hours |
| SalaryComponent | id, employee\_id, component\_name, value\_type (fixed/percentage\_of\_wage), value, computed\_amount |

Auto-calculation rule: any percentage-based component recomputes automatically whenever monthly\_wage (or the component it's a percentage of) changes. Validation: sum of computed\_amount across all components must not exceed monthly\_wage.

## 3.7 Onboarding

| **Table** | **Key Fields** |
| --- | --- |
| OnboardingTemplate | id, role, task\_list (JSON: [{task\_name, due\_offset\_days}]), doc\_links (JSON) |
| OnboardingTask | id, employee\_id, task\_name, due\_date, status (pending/done), completed\_at |

## 3.8 Gamification

| **Table** | **Key Fields** |
| --- | --- |
| Badge | id, name, description, criteria\_type (reliability\_streak/planning\_discipline/peer\_nominated) |
| EmployeeBadge | employee\_id, badge\_id, awarded\_at, period |
| Vote | id, voter\_id, nominee\_id, title, period, voter\_role (used for weighting: admin multiplier applied at tally time) |

## 3.9 Notification

| **Table** | **Key Fields** |
| --- | --- |
| Notification | id, user\_id, title, message, category, read (bool), created\_at |

# 4. API Surface (Representative Endpoints)

| **Method & Path** | **Module** | **Access** | **Purpose** |
| --- | --- | --- | --- |
| POST /auth/signup | Auth | Admin/HR | Create a new employee account, auto-generate Login ID + system password |
| POST /auth/login | Auth | Public | Authenticate, issue JWT |
| GET /employees | Employee | All (scoped) | List employee cards (self only for Employee role) |
| PATCH /employees/{id}/self-serve | Employee | Self | Instant update of low-risk fields |
| PATCH /employees/{id}/request-edit | Employee | Self | Create a Change Request for a verified field |
| GET /employees/change-requests | Employee | Admin/HR | Pending edit requests, diff view |
| POST /employees/change-requests/{id}/approve | Employee | Admin/HR | Approve and apply a pending edit |
| POST /attendance/check-in | Attendance | Self | Mark check-in, sets status dot to green |
| POST /attendance/check-out | Attendance | Self | Mark check-out, computes work\_hours/extra\_hours |
| GET /attendance/me | Attendance | Self | Day/week attendance view |
| GET /attendance | Attendance | Admin/HR | All-employee attendance, filterable |
| POST /leave/apply | Leave | Self | Standard leave request (pending) |
| POST /leave/apply/emergency | Leave | Self | Emergency leave, auto-provisional |
| POST /leave/{id}/approve | Leave | Admin/HR | Approve, update balance |
| POST /leave/{id}/flag-provisional | Leave | Admin/HR | Retroactive review of an emergency leave |
| GET /payroll/me | Payroll | Self | Read-only full salary breakdown |
| PATCH /payroll/{employee\_id} | Payroll | Admin | Creates 30-day Change Requests per field |
| POST /payroll/{employee\_id}/correct | Payroll | Admin | Immediate correction, flagged separately |
| POST /payroll/change-requests/{id}/acknowledge | Payroll | Self | Employee receipt of an upcoming change |
| GET /onboarding/me | Onboarding | Self | New hire's checklist and progress |
| GET /gamification/leaderboard | Gamification | All | Opt-in reliability/recognition board |
| POST /gamification/vote | Gamification | All | Cast a weighted monthly/yearly vote |
| POST /simulate/leave-impact | Simulation | Admin/HR | Deterministic what-if calculation |
| POST /simulate/resignation-impact | Simulation | Admin/HR | Deterministic resignation impact |
| POST /chatbot/ask | Chatbot | Admin/HR | Free-text question → parsed intent → simulation → natural-language reply |
| GET /notifications | Notification | Self | In-app notification list |

# 5. The Change Request Pattern (Shared Logic)

Both Payroll changes (Section 7.1 of the concept doc) and Employee verified-field edits (Section 7.2) reuse a single shared implementation rather than duplicating approval logic.

class ChangeRequest(Base):
 id: int
 entity\_type: str # "payroll" | "employee\_profile"
 entity\_id: int
 field\_name: str
 old\_value: str
 new\_value: str
 status: str # pending | approved | rejected
 effective\_date: date | None # None = immediate (employee edits)
 reason: str | None
 requested\_by: int
 approved\_by: int | None
 is\_correction: bool = False
 created\_at: datetime
 resolved\_at: datetime | None

* create\_change\_request(entity\_type, entity\_id, field, old, new, effective\_date, reason) — used by both Payroll and Employee modules
* approve\_change\_request(id, approved\_by) / reject\_change\_request(id, approved\_by, reason)
* apply\_due\_changes() — called daily by the scheduler; finds status=approved (or pending with a reached effective\_date, per module's configured flow) rows whose effective\_date <= today and writes them into the owning module's live table via that module's own apply function, keeping the shared module free of module-specific write logic

# 6. Simulation Engine Design

## 6.1 Inputs

* Department headcount and role distribution (Employee module)
* Historical and current attendance rates (Attendance module, via get\_attendance\_summary())
* Active and historical leave records (Leave module, via get\_approved\_leave\_count())

## 6.2 Computation (Deterministic, No ML)

* availability\_pct = 1 - (currently\_on\_leave + projected\_leave) / department\_headcount
* workload\_redistribution: proportionally distributes the absent headcount's typical workload across remaining team members, flagged per role where redistribution exceeds a configurable overload threshold
* department\_capacity: availability\_pct weighted by role criticality (roles marked business-critical lower the safe capacity threshold)
* bottlenecks: any team/role where projected availability drops below the configured threshold (default 70%) is returned as a named bottleneck

## 6.3 Output Schema

class SimulationResult(BaseModel):
 availability\_pct: float
 workload\_redistribution: dict[str, float] # role -> extra load %
 department\_capacity: float
 attendance\_impact: dict
 bottlenecks: list[str]

# 7. Chatbot / Ollama Integration

## 7.1 Flow

* 1. User sends free-text question to POST /chatbot/ask
* 2. parse\_intent(question) calls Ollama with format="json", extracting {action, department, percentage, timeframe}
* 3. The parsed intent is validated against the Simulation module's request schema before use
* 4. The relevant simulation\_service function is called in-process (same Pydantic contract as the REST endpoint)
* 5. humanize\_result(result) calls Ollama again, instructed to phrase the structured JSON as natural language without introducing any figures not present in the input
* 6. Response returns both the natural-language reply and the raw structured data, so the frontend can show both

## 7.2 Client Implementation

# modules/chatbot/ollama\_client.py
import httpx

async def query\_ollama(prompt: str, model: str = "llama3.2:3b", json\_mode: bool = False) -> str:
 payload = {"model": model, "prompt": prompt, "stream": False}
 if json\_mode:
 payload["format"] = "json"
 async with httpx.AsyncClient(timeout=60) as client:
 resp = await client.post("http://ollama:11434/api/generate", json=payload)
 return resp.json()["response"]

## 7.3 Safeguards

* If parse\_intent() returns an incomplete or invalid structure, the endpoint asks a clarifying question instead of guessing missing parameters
* Simulation numbers are never produced by the model — only by the deterministic engine — keeping every figure shown to HR traceable back to a specific query
* Conversation logs (question, parsed intent, result, reply) are retained for debugging and demo verification

# 8. Scheduled Jobs (APScheduler)

| **Job** | **Frequency** | **Action** |
| --- | --- | --- |
| apply\_due\_changes() | Daily | Applies Payroll & Employee change requests whose effective\_date has arrived |
| leave\_sla\_escalation() | Hourly | Notifies secondary approver for standard leave pending beyond threshold |
| mark\_absent() | Daily (end of day) | Marks employees with no check-in and no approved leave as Absent |
| gamification\_tally() | Monthly / Yearly | Tallies weighted votes, awards badges/titles |

# 9. Security Model

* JWT-based auth; token carries user id and role, verified via a shared FastAPI dependency on every protected route
* Role dependencies: require\_admin(), require\_self\_or\_admin(employee\_id) applied per-route
* Payroll and bank/verified-profile data require elevated (Admin) permission for any write
* All Change Request approvals, payroll corrections, and leave decisions are audit-logged (who, what, when, old/new value)
* Rate limiting applied to /auth/login and /chatbot/ask
* No employee data leaves local infrastructure — Ollama runs on-premises, no external LLM API calls

# 10. Deployment (Docker Compose)

services:
 app:
 build: .
 ports: ["8000:8000"]
 depends\_on: [postgres, ollama]
 environment:
 - DATABASE\_URL=postgresql://dayflow:pass@postgres:5432/dayflow
 - OLLAMA\_HOST=http://ollama:11434
 - PAYROLL\_NOTICE\_DAYS=30
 - LEAVE\_SLA\_HOURS=24
 postgres:
 image: postgres:16
 environment:
 - POSTGRES\_DB=dayflow
 - POSTGRES\_USER=dayflow
 - POSTGRES\_PASSWORD=pass
 volumes: ["pgdata:/var/lib/postgresql/data"]
 ollama:
 image: ollama/ollama
 volumes: ["ollamadata:/root/.ollama"]
volumes:
 pgdata:
 ollamadata:

# 11. Future Extraction Path

If Dayflow needs to move beyond a single-team, single-deploy POC, the modules with the cleanest boundaries and the strongest independent reasons to separate should be extracted first, in this order:

* Simulation — stateless, pure compute, no writes; easiest to lift out with no data-migration concerns
* Payroll — sensitive data, natural candidate for isolation and stricter network/access controls
* Auth — typically the first true dependency every other service needs, common to extract early in real systems

Employee, Attendance, Leave, Onboarding, and Gamification share enough employee-context that they can remain fused far longer without meaningful cost.