**Dayflow**

**Implementation Plan**

Step-by-step build order, in complete detail, checkbox tracked

# How To Use This Plan

Steps are ordered by dependency — later steps assume earlier ones are complete. Each step lists exactly what to build, the reasoning behind the order, and a checklist of concrete sub-tasks. Check items off as completed. Architecture follows the modular monolith design agreed on: FastAPI, one deployable app, one shared Postgres database with per-module table ownership.

***Note:*** *Frontend build-out is intentionally kept light in this plan since the stated focus is backend; each backend step notes the minimum frontend contract it must expose.*

# Phase 0 — Foundations

**Step 0.1: Project Scaffolding**

**☐** Initialize FastAPI project with the modular monolith folder structure: /app/core, /app/shared, /app/modules/{auth,employee,attendance,leave,payroll,gamification,simulation,chatbot,notification}

**☐** Set up SQLAlchemy engine/session in /app/core/database.py, pointed at a single Postgres instance

**☐** Set up /app/core/config.py using Pydantic Settings, loading from .env (DB URL, JWT secret, Ollama host, notice-period-days, SLA thresholds)

**☐** Set up Alembic for migrations, with one migration history shared across all module schemas

**☐** Create /app/main.py that mounts all module routers with clear prefixes (/auth, /employees, /attendance, /leave, /payroll, /gamification, /simulate, /chatbot)

**☐** Add global exception handlers and a consistent error-response schema

**☐** Add CORS middleware for the frontend origin

**☐** Docker Compose file with two services: the FastAPI app and Postgres (add Ollama as a third service once Phase 8 begins)

**Step 0.2: Shared Change Request Module**

Built first because both Payroll (Step 5) and Employee Profile (Step 2) depend on it — building it once now avoids duplicating the approval/diff logic later.

**☐** Create /app/shared/change\_request/models.py with the ChangeRequest table: id, entity\_type, entity\_id, field\_name, old\_value, new\_value, status (pending/approved/rejected), effective\_date (nullable), requested\_by, approved\_by (nullable), reason, created\_at, resolved\_at

**☐** Create service functions: create\_change\_request(), approve\_change\_request(), reject\_change\_request(), get\_pending\_for\_entity(), apply\_due\_changes()

**☐** apply\_due\_changes() is the function a scheduled job will call daily to auto-apply changes whose effective\_date has passed

**☐** Write unit tests for the create → approve → apply lifecycle and the create → reject lifecycle, independent of any specific module using it

**Step 0.3: Notification Module (Minimal Version)**

**☐** Create /app/modules/notification/service.py with a single notify(user\_id, title, message, category) function

**☐** Start with in-app notifications only (a Notification table: id, user\_id, title, message, category, read, created\_at) — email/push can be added later without changing the interface

**☐** Expose GET /notifications and PATCH /notifications/{id}/read for the frontend

***Note:*** *Every later module (Payroll, Employee, Leave) calls notification\_service.notify(...) rather than implementing its own alert logic.*

# Phase 1 — Authentication & Authorization

**Step 1: Auth Module**

Built first because every other module depends on knowing who the current user is and what role they hold.

**☐** User table: id, login\_id, email, password\_hash, role (admin/hr/employee), must\_change\_password, created\_at

**☐** Implement the Login ID generation algorithm: Company code + first two letters of first & last name + year of joining + serial number of joining, e.g. 0C210C202A0001

**☐** Implement POST /auth/signup — restricted to Admin/HR callers only (no public self-registration), generates Login ID and a system password

**☐** Implement POST /auth/login — verifies credentials, issues a JWT containing user id + role

**☐** Implement password hashing (bcrypt/argon2) and a force-password-change flow on first login

**☐** Implement JWT verification dependency in /app/core/security.py, reusable via FastAPI's Depends() across every module

**☐** Implement role-based dependency helpers: require\_admin(), require\_self\_or\_admin(employee\_id)

**☐** Write tests: signup by non-admin is rejected, login with wrong password is rejected with a generic error, valid login returns a usable token

# Phase 2 — Employee Profile Module

**Step 2: Employee Module + Edit Verification**

**☐** Employee table: id, user\_id (FK to Auth), name, dob, doj, department, designation, manager\_id, phone, address, personal\_email, marital\_status, profile\_picture\_url, about, skills (JSON), certifications (JSON), hobbies (JSON)

**☐** Implement GET /employees (Admin: all employees as cards; Employee: self only)

**☐** Implement GET /employees/{id} — view-only mode for other employees' cards, full edit mode for self/admin

**☐** Split editable fields into Self-Serve (profile\_picture, about, hobbies, skills) vs Verified (phone, address, emergency\_contact, bank\_details)

**☐** Implement PATCH /employees/{id}/self-serve — applies instantly, no approval needed

**☐** Implement PATCH /employees/{id}/request-edit — for Verified fields, calls shared change\_request\_service.create\_change\_request() instead of writing directly

**☐** Implement Admin endpoints: GET /employees/change-requests (pending list with diff view: old vs new), POST /employees/change-requests/{id}/approve, POST /employees/change-requests/{id}/reject (reason required)

**☐** On approval, apply the change to the Employee table and call notification\_service.notify() to the employee

**☐** On rejection, notify the employee with the admin's reason, record stays unchanged

**☐** Frontend contract: profile page needs a visible “pending change” indicator per field awaiting approval

# Phase 3 — Attendance Module

**Step 3: Attendance Module**

**☐** Attendance table: id, employee\_id, date, check\_in\_time, check\_out\_time, status (present/absent/half-day/leave), work\_hours, extra\_hours, source (office/field)

**☐** Implement POST /attendance/check-in and POST /attendance/check-out for the current authenticated employee

**☐** Auto-compute work\_hours and extra\_hours on check-out based on the org's defined working hours (from Payroll config, Step 5)

**☐** Implement GET /attendance/me?month=&view=day|week for employee self-view

**☐** Implement GET /attendance?date=&employee\_id= for Admin/HR view of all employees on a given day, with search/filter

**☐** Implement a status-derivation job: at end of day, any employee with no check-in and no approved leave is marked Absent

**☐** Implement field-based attendance inference (status derived from assigned tasks) as a configurable alternate source per employee, for non-office-based roles

**☐** Expose an internal service function get\_attendance\_summary(employee\_id, date\_range) for Payroll (Step 5) and Simulation (Step 8) to consume — other modules must call this, never query the Attendance table directly

# Phase 4 — Leave & Time-Off Module

**Step 4: Leave Module + Emergency Fast-Track + SLA Escalation**

**☐** LeaveRequest table: id, employee\_id, leave\_type (paid/sick/unpaid/emergency), start\_date, end\_date, status (pending/provisional/approved/rejected), attachment\_url, remarks, requested\_at, resolved\_at, resolved\_by

**☐** LeaveBalance table: employee\_id, leave\_type, allocated\_days, used\_days, remaining\_days (recomputed on approval)

**☐** Implement POST /leave/apply for standard leave types (paid/sick/unpaid) → status = pending

**☐** Implement POST /leave/apply/emergency — separate endpoint, status is immediately set to provisional and the leave is instantly reflected in attendance as Leave, no wait required

**☐** Implement GET /leave/me and GET /leave (Admin/HR, all employees, filterable) with Approve/Reject actions

**☐** Implement POST /leave/{id}/approve and POST /leave/{id}/reject (comment required on reject), updating LeaveBalance accordingly

**☐** Implement the provisional-leave review window: Admin can flag/reject a provisional leave within a configurable window (e.g. 48 hours) via POST /leave/{id}/flag-provisional, which opens a review thread instead of instantly reversing attendance

**☐** Implement the abuse-prevention cap: track provisional-emergency-leave count per employee per rolling period; once the cap is hit, POST /leave/apply/emergency for that employee behaves like standard leave (status = pending) until the period resets

**☐** Implement the SLA escalation job (scheduled, e.g. hourly): find leave requests with status = pending older than the configured threshold, and call notification\_service.notify() to the requester's manager/secondary approver

**☐** Wire leave approval/rejection to call notification\_service.notify() for the employee

# Phase 5 — Payroll Module

**Step 5: Payroll Module + 30-Day Notice Workflow**

**☐** SalaryStructure table: employee\_id, wage\_type (fixed/percentage), monthly\_wage, yearly\_wage, working\_days\_per\_week, base\_time\_hours

**☐** SalaryComponent table: id, employee\_id, component\_name, value\_type (fixed/percentage\_of\_wage), value, computed\_amount

**☐** Implement the auto-calculation logic: whenever monthly\_wage or a percentage-based component changes, recompute all dependent component amounts (e.g. Basic = 60% of wage, HRA = 50% of Basic)

**☐** Enforce validation: sum of all components must not exceed the defined wage — reject the save with a clear error otherwise

**☐** Implement GET /payroll/me (employee, read-only full breakdown) and GET /payroll/{employee\_id} (admin, full control)

**☐** Implement PATCH /payroll/{employee\_id} for Admin — instead of writing directly, calls change\_request\_service.create\_change\_request() per changed field with effective\_date = today + NOTICE\_PERIOD\_DAYS (config, default 30)

**☐** Update the employee Salary Info view to show Current vs Upcoming (effective DD/MM/YYYY) values side by side when a pending change exists

**☐** Implement optional employee acknowledgment: POST /payroll/change-requests/{id}/acknowledge (receipt only, does not block or approve)

**☐** Implement the Immediate Correction override: POST /payroll/{employee\_id}/correct — applies instantly but writes a distinctly-flagged audit log entry (is\_correction = true) separate from routine change requests

**☐** Add apply\_due\_changes() (from the shared module, Step 0.2) to the daily scheduled job so payroll changes go live automatically once effective\_date arrives

**☐** Wire creation of a payroll change request to call notification\_service.notify() immediately

# Phase 6 — Onboarding & KT (Lightweight)

**Step 6: Onboarding Checklist Module**

**☐** OnboardingTemplate table (per role/department): id, role, task\_list (JSON: task name, default due offset in days)

**☐** OnboardingTask table (per new hire): id, employee\_id, task\_name, due\_date, status (pending/done), completed\_at

**☐** On new employee creation (Step 1 signup), auto-instantiate OnboardingTask rows from the matching OnboardingTemplate

**☐** Implement GET /onboarding/me and PATCH /onboarding/tasks/{id} (mark done) for the new hire

**☐** Implement GET /onboarding/{employee\_id} progress view for Admin/HR

**☐** Add a buddy\_id (mentor) field to the Employee table (Step 2) and an admin endpoint to assign it

**☐** Add a doc\_links (JSON array of tagged links) field on OnboardingTemplate for role-specific knowledge base references

# Phase 7 — Gamification Module

**Step 7: Recognition & Badges**

**☐** Badge table: id, name, description, criteria\_type (reliability\_streak/planning\_discipline/peer\_nominated)

**☐** EmployeeBadge table: employee\_id, badge\_id, awarded\_at, period (month/year)

**☐** Implement the reliability-streak calculator: consecutive periods with zero unapproved/unplanned absence, explicitly excluding approved Sick Leave and Emergency Leave from breaking the streak (reads from Attendance + Leave service functions, never their tables directly)

**☐** Implement the planning-discipline metric: average advance-notice days on approved standard leave requests

**☐** Vote table: voter\_id, nominee\_id, title, period, voter\_role (weighting applied at tally time: admin vote = configurable multiplier, e.g. 3x a peer vote)

**☐** Implement POST /gamification/vote and a scheduled monthly/yearly tally job that awards titles based on weighted vote totals

**☐** Implement an opt-in flag per employee (visible\_on\_leaderboard) respected by all leaderboard/read endpoints

**☐** Implement GET /gamification/leaderboard and GET /gamification/me/badges

# Phase 8 — Simulation Engine (Deterministic Core)

**Step 8: What-If Simulation Engine**

Pure computation, no AI involved in this step — this is the trustworthy core the chatbot will sit on top of in Phase 9.

**☐** Define the request/response Pydantic schemas: SimulationRequest (type: leave\_impact | resignation\_impact, department, percentage/count, timeframe) and SimulationResult (availability\_pct, workload\_redistribution, department\_capacity, attendance\_impact, bottlenecks: list)

**☐** Implement calculate\_leave\_impact(db, department, percentage, timeframe): pulls current headcount and historical attendance/leave rates via Employee/Attendance/Leave service functions (never raw table queries across module boundaries), computes projected availability and flags departments/roles dropping below a capacity threshold

**☐** Implement calculate\_resignation\_impact(db, employee\_ids or count, department): estimates redistributed workload and capacity loss based on role criticality and current headcount

**☐** Implement bottleneck detection: flag any team/role where projected availability falls below a configurable threshold (e.g. 70%)

**☐** Expose POST /simulate/leave-impact and POST /simulate/resignation-impact, both Admin/HR only

**☐** Write test cases with known sample data to confirm the math is correct — this is the layer that must be demonstrably accurate, so cover it well

# Phase 9 — Chatbot Module (Ollama Integration)

**Step 9: Local SLM Chatbot Wrapper**

**☐** Add Ollama as a service in Docker Compose; pull a small quantized model (e.g. llama3.2:3b or phi3:mini)

**☐** Implement /app/modules/chatbot/ollama\_client.py with an async query\_ollama(prompt, model, format='json') helper using httpx.AsyncClient

**☐** Implement parse\_intent(question: str) -> dict: prompts the model to extract {action, department, percentage/count, timeframe} as structured JSON from a free-text HR question

**☐** Implement humanize\_result(result: SimulationResult) -> str: prompts the model to phrase the structured simulation output as a natural-language answer, explicitly instructed not to introduce numbers not present in the input JSON

**☐** Implement POST /chatbot/ask: question in → parse\_intent() → call simulation\_service functions directly (in-process call, same schema as the REST contract) → humanize\_result() → return {reply, data} so the frontend can show both the sentence and the raw numbers

**☐** Add a fallback path: if parse\_intent() returns an incomplete/ambiguous structure, respond asking a clarifying question rather than guessing parameters

**☐** Add basic conversation logging (question, parsed intent, result, reply) for debugging and demo purposes

**☐** Load-test response latency with the chosen model on target hardware; drop to a smaller quantization if the demo needs faster turnaround

# Phase 10 — Cross-Cutting Hardening

**Step 10: Security, Scheduling, and Polish**

**☐** Wire up APScheduler (in-process) for all scheduled jobs: apply\_due\_changes() (Payroll + Employee), leave SLA escalation, attendance absent-marking, gamification monthly/yearly tally

**☐** Review every endpoint against the role matrix (Admin/HR vs Employee) and confirm require\_admin()/require\_self\_or\_admin() is applied correctly everywhere

**☐** Add audit logging across Change Request approvals, payroll corrections, and leave approvals (who, what, when)

**☐** Add rate limiting on /auth/login and /chatbot/ask

**☐** Write integration tests covering the full payroll change lifecycle and the full employee-edit-verification lifecycle end-to-end

# Phase 11 — Demo Preparation

**Step 11: Seed Data & Demo Script**

**☐** Write a seed script creating a realistic sample org: multiple departments, employees with varied attendance/leave history so the Simulator has meaningful data to compute against

**☐** Prepare 3–5 chatbot demo questions with known-correct expected answers, verified against the Simulation Engine's own test cases

**☐** Prepare a short walkthrough covering: emergency leave fast-track, payroll 30-day notice view, employee edit verification diff view, gamification leaderboard, and the What-If chatbot

**☐** Dry-run the full demo end-to-end at least once before presenting