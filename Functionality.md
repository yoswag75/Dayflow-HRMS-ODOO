# Dayflow HRMS - Functional Scope

> **Purpose:** This is the single living checklist for the Dayflow Human Resource Management System. Update it whenever the team adds, changes, or removes a feature.

## 1. Product Goal

Dayflow is a role-based Human Resource Management System for employees and HR/Admin staff. It centralizes employee information, attendance, leave requests, payroll visibility and controlled changes, onboarding, recognition, workforce simulations, chatbot-assisted analysis, and notifications.

## 2. Roles and Access

| Capability | Employee | HR/Admin |
| --- | --- | --- |
| Sign in and change a system-issued password | Yes | Yes |
| Create employee accounts | No | Yes |
| View own profile | Yes | Yes |
| Edit own contact/profile image | Yes | Yes |
| Edit any employee profile | No | Yes |
| View own attendance | Yes | Yes |
| View all attendance | No | Yes |
| Check in / check out | Yes | Yes, if required |
| Request time off | Yes | Yes, if required |
| Approve or reject time off | No | Yes |
| View own salary | Optional/read-only | Yes |
| View or update all salaries | No | Yes |
| Complete onboarding tasks | Yes | View progress |
| View recognition points and badges | Yes | Yes |
| Run workforce simulations and use the HR chatbot | No | Yes |
| Manage notification preferences | Yes | Yes |

## 3. Core Features

### 3.1 Authentication

- [ ] Admin/HR account-creation form; public self-registration is not supported.
- [ ] Generate the employee login ID and temporary system password during account creation.
- [ ] Force a password change on first login.
- [ ] Client-side validation and clear field-level errors.
- [ ] Password visibility toggle and password-strength rules.
- [ ] Sign-in with the backend-issued login ID or supported credential.
- [ ] Invalid-credential error state.
- [ ] Redirect to the correct post-login landing page.
- [ ] Sign-out action.
- [ ] Persist and restore authenticated session safely.

### 3.2 Role-based navigation

- [ ] Global navigation for Employees, Attendance, Time Off, and profile menu.
- [ ] Show only actions permitted for the signed-in role.
- [ ] Profile menu: My Profile, Edit Profile, and Log Out.
- [ ] Guard restricted routes and display a friendly unauthorized state.

### 3.3 Employee directory - HR/Admin

- [ ] Employee-card or table view after login for HR/Admin.
- [ ] Employee summary: profile photo, name, employee ID, role/title, and current status.
- [ ] Search employees by name, employee ID, or department.
- [ ] Filter employees by relevant status or department when available.
- [ ] Open an employee profile from the directory.
- [ ] Empty, loading, and failure states.

### 3.4 Employee profile

- [ ] Profile header: photo, full name, employee ID, email, phone, job title, manager, department, and location.
- [ ] Private information section.
- [ ] Resume/about section.
- [ ] Skills section.
- [ ] Certifications section.
- [ ] Employee self-serve fields such as profile photo, about, hobbies, and skills update immediately.
- [ ] Verified fields such as phone, address, emergency contact, and bank details create a change request instead of updating immediately.
- [ ] Show pending verified-field changes and their old/new values.
- [ ] HR/Admin can edit all employee details.
- [ ] HR/Admin can approve or reject employee change requests and supply a rejection reason.
- [ ] Salary information is visible only to the authorized role.

### 3.5 Attendance

- [ ] Check-in action.
- [ ] Check-out action.
- [ ] Current attendance status: present, absent, half-day, or on leave.
- [ ] Prevent invalid actions, such as checking out before checking in or checking in twice.
- [ ] Employee attendance view: only the signed-in employee's records.
- [ ] HR/Admin attendance view: all employee records.
- [ ] Daily and weekly attendance views.
- [ ] Attendance table: employee, date, check-in, check-out, total hours, and status.
- [ ] Loading, no-records, and API-error states.

### 3.6 Time off / leave

- [ ] Employee leave-request form.
- [ ] Leave types: paid leave, sick leave, unpaid leave, and emergency leave.
- [ ] Select start and end dates using a calendar.
- [ ] Add an optional reason/remarks field.
- [ ] Validate date ranges and prevent invalid submissions.
- [ ] Request status: pending, approved, or rejected.
- [ ] Employee can view their own leave requests and status.
- [ ] HR/Admin can view all leave requests.
- [ ] HR/Admin can approve or reject a request and add comments.
- [ ] Emergency leave is provisional immediately, subject to a review window and abuse-prevention cap.
- [ ] Escalate standard leave requests that exceed the configured approval SLA.
- [ ] Update the UI immediately after a decision, using the backend response as the source of truth.

### 3.7 Salary and payroll visibility

- [ ] Employee salary view, only if included in the final scope, is read-only and limited to their own data.
- [ ] HR/Admin salary view shows salary structure and payroll components.
- [ ] HR/Admin can update salary details only if the backend supports it.
- [ ] Routine payroll edits create change requests with a default 30-day effective period.
- [ ] Show current and upcoming payroll values side by side when a change is pending.
- [ ] Employees can acknowledge upcoming payroll changes without approving or blocking them.
- [ ] Admin can apply an immediate correction that remains separately audit-flagged.
- [ ] Never expose another employee's salary data to an employee.

### 3.8 Onboarding

- [ ] Show the current employee's onboarding checklist, due dates, and progress.
- [ ] Allow the employee to mark onboarding tasks complete.
- [ ] Allow HR/Admin to view an employee's onboarding progress.
- [ ] Support role/department templates, buddy assignment, and knowledge-transfer links.

### 3.9 Recognition and gamification

- [ ] Show an opt-in leaderboard with department and period filters.
- [ ] Show the current employee's points history and earned badges.
- [ ] Support weighted monthly/yearly recognition voting.
- [ ] Exclude approved sick and emergency leave from reliability penalties.

### 3.10 Workforce simulation

- [ ] Let Admin/HR run leave-impact or resignation-impact simulations.
- [ ] Show availability, workload redistribution, department capacity, attendance impact, and bottlenecks.
- [ ] Show simulation history for authorized users.
- [ ] Treat deterministic backend calculations—not AI-generated figures—as the numeric source of truth.

### 3.11 HR chatbot

- [ ] Let Admin/HR create a chat session and send workforce questions.
- [ ] Render streaming chatbot replies and retain session history.
- [ ] Show structured simulation data alongside the natural-language response when supplied.
- [ ] Ask a clarifying question when the backend cannot safely parse the requested scenario.

### 3.12 Notifications

- [ ] Show the current user's in-app notifications.
- [ ] Mark individual notifications as read.
- [ ] View and update notification preferences.

## 4. Frontend Standards

- [ ] Responsive layouts for desktop and mobile.
- [ ] Accessible labels, keyboard navigation, readable contrast, and clear focus states.
- [ ] Consistent loading, empty, success, and error states on every data screen.
- [ ] Confirmation or clear feedback after check-in/out, leave submission, and leave decision actions.
- [ ] Do not make API calls directly from UI components; use one typed API/service layer.
- [ ] Use mocked API handlers until each real backend endpoint is ready.

## 5. Backend Integration Contract

- [ ] Maintain all endpoint paths, payloads, response objects, error shapes, and role requirements in `api.yaml`.
- [ ] Agree authentication mechanism and token/session lifecycle.
- [ ] Define a single current-user response that includes the user's role and permissions.
- [ ] Define pagination, sorting, filtering, and date formats before implementing list screens.
- [ ] Version or communicate breaking API changes before merging them.
- [ ] Frontend mocks and backend responses must match `api.yaml`.

### 5.1 Contract alignment decisions

- `api.yaml` is the canonical API contract. Backend route choices take precedence over legacy route names in older planning documents.
- Notification routes use `/notifications/me`, `/notifications/{id}/read`, and `/notifications/preferences`.
- Simulation routes use `/simulation/run` and `/simulation/history/{user_id}`; legacy `/simulate/leave-impact` and `/simulate/resignation-impact` aliases are retired.
- Chatbot routes use `/chatbot/session`, `/chatbot/message`, and `/chatbot/session/{id}/history`; legacy `/chatbot/ask` is retired.
- Non-conflicting planned routes from `Docs/Implementation.md` remain in the contract.

### 5.2 Current backend repository status

- The backend is planned as a FastAPI modular monolith using PostgreSQL, SQLAlchemy/Alembic, JWT authentication, APScheduler, and Ollama.
- Scaffolds currently exist for core services, Auth, Change Request, Notification, Gamification, Simulation, and Chatbot.
- Employee, Attendance, Leave, Payroll, and Onboarding implementation folders are not yet present.
- Existing backend application, router, service, model, and schema files are placeholders; frontend work must use mocks until implemented routes match `api.yaml`.

## 6. Suggested Delivery Order

1. [ ] Finalize shared request/response/error schemas in `api.yaml`.
2. [ ] Build application shell, navigation, sign-in, and route guards with mocks.
3. [ ] Build employee directory and profile screens.
4. [ ] Build attendance flows and views.
5. [ ] Build leave-request and approval flows.
6. [ ] Build salary visibility screens.
7. [ ] Build onboarding, notifications, recognition, simulation, and chatbot experiences with mocks.
8. [ ] Connect real API endpoints incrementally and test each workflow end-to-end.
9. [ ] Add responsive, accessibility, error-state, and demo polish.

## 7. Not in the MVP Unless Time Allows

- [ ] Analytics and reporting dashboard.
- [ ] Salary-slip generation or download.
- [ ] Document upload/storage.
- [ ] Advanced payroll calculations.
- [ ] Audit history and detailed activity logs.

## 8. Change Log

| Date | Change | Owner | Decision / Notes |
| --- | --- | --- | --- |
| 2026-08-22 | Initial functional scope created from the requirements brief and UI board. | Team | Confirm final API contract before implementation. |
| 2026-08-22 | Aligned functional scope with `backend/README.md`, `Docs/Implementation.md`, and `Docs/Tech_details.md`; added change-request, emergency leave, payroll notice, onboarding, gamification, simulation, chatbot, and notification requirements. | Codex | Backend-selected Notification, Simulation, and Chatbot route designs supersede legacy route names. |
| 2026-08-22 | Recorded current backend scaffold status and mock-first frontend requirement. | Codex | Backend implementation is not yet available for live integration. |
