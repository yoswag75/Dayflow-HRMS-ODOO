# Dayflow HRMS — Odoo Hackathon

A Human Resource Management System built on Odoo, designed for small-to-mid-size teams.

## Modules

| Module | Description |
|---|---|
| Employee | Core employee records, departments, job positions |
| Attendance | Clock-in/out, shift scheduling, overtime tracking |
| Leave | Leave requests, approvals, balance tracking |
| Payroll | Salary structure, payslip generation, statutory deductions |
| Recruitment | Job postings, applicant pipeline, interview scheduling |
| Appraisal | Performance review cycles, KPI tracking |

## Tech Stack

- **Backend:** Odoo 17 (Python)
- **Frontend:** Odoo Web Client (OWL)
- **DB:** PostgreSQL
- **API:** REST via `api.yaml`

## Setup

```bash
# Clone and install dependencies
git clone <repo>
cd Dayflow-HRMS-ODOO

# Start Odoo instance (Docker)
docker compose up -d

# Access at http://localhost:8069
```

## Team

Built for the ODOO Hackathon — Dayflow team.
