# Dayflow HRMS - Functional Scope

> **Purpose:** This is the single living checklist for the Dayflow Human Resource Management System. Update it whenever the team adds, changes, or removes a feature.

## 1. Product Goal

Dayflow is a role-based Human Resource Management System for employees and HR/Admin staff. It centralizes employee information, attendance, leave requests, and salary visibility.

## 2. Roles and Access

| Capability | Employee | HR/Admin |
| --- | --- | --- |
| Sign up and sign in | Yes | Yes |
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

## 3. Core Features

### 3.1 Authentication and onboarding

- [ ] Sign-up form: employee ID, company name, manager/HR contact where required, email, phone number, password, confirm password, and role.
- [ ] Client-side validation and clear field-level errors.
- [ ] Password visibility toggle and password-strength rules.
- [ ] Email verification flow, if supplied by the backend.
- [ ] Sign-in with email and password.
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
- [ ] Employee can edit only permitted personal fields: contact details and profile photo.
- [ ] HR/Admin can edit all employee details.
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
- [ ] Leave types: paid leave, sick leave, and unpaid leave.
- [ ] Select start and end dates using a calendar.
- [ ] Add an optional reason/remarks field.
- [ ] Validate date ranges and prevent invalid submissions.
- [ ] Request status: pending, approved, or rejected.
- [ ] Employee can view their own leave requests and status.
- [ ] HR/Admin can view all leave requests.
- [ ] HR/Admin can approve or reject a request and add comments.
- [ ] Update the UI immediately after a decision, using the backend response as the source of truth.

### 3.7 Salary and payroll visibility

- [ ] Employee salary view, only if included in the final scope, is read-only and limited to their own data.
- [ ] HR/Admin salary view shows salary structure and payroll components.
- [ ] HR/Admin can update salary details only if the backend supports it.
- [ ] Never expose another employee's salary data to an employee.

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

## 6. Suggested Delivery Order

1. [ ] Finalize roles, API contract, and shared data shapes.
2. [ ] Build application shell, navigation, sign-in, and route guards with mocks.
3. [ ] Build employee directory and profile screens.
4. [ ] Build attendance flows and views.
5. [ ] Build leave-request and approval flows.
6. [ ] Build salary visibility screens.
7. [ ] Connect real API endpoints incrementally and test each workflow end-to-end.
8. [ ] Add responsive, accessibility, error-state, and demo polish.

## 7. Not in the MVP Unless Time Allows

- [ ] Email or in-app notifications.
- [ ] Analytics and reporting dashboard.
- [ ] Salary-slip generation or download.
- [ ] Document upload/storage.
- [ ] Advanced payroll calculations.
- [ ] Audit history and detailed activity logs.

## 8. Change Log

| Date | Change | Owner | Decision / Notes |
| --- | --- | --- | --- |
| 2026-08-22 | Initial functional scope created from the requirements brief and UI board. | Team | Confirm final API contract before implementation. |
