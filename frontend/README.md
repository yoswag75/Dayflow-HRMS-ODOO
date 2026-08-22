# Dayflow frontend

A responsive React frontend for the HR management system. All application data is loaded from the backend API; there is no production mock-data fallback.

## Run locally

```bash
cd backend
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite serves the application at `http://localhost:5173` by default.

## API configuration

Copy the example environment file and point it to the running FastAPI service:

```bash
cp .env.example .env
```

The default API URL is `http://localhost:8000`. Authentication and all protected requests use the backend-issued bearer token.

Open `http://localhost:5173/setup` on a fresh database to create the first administrator. No demo users or runtime fixtures are created. The administrator can then onboard employees and securely share each generated temporary password.

## Connected functionality

- First administrator setup, email login, logout, and required password change
- Employee onboarding, directory, and read-only profiles
- Employee check-in/check-out and HR attendance listing
- Employee leave requests and HR approval/rejection
- Employee onboarding checklist
- Recognition leaderboard, headcount simulation, chatbot, and notifications

Payroll visibility, profile editing, employee change requests, emergency-leave fast-track, and recognition voting are intentionally unavailable until matching backend routes exist.

## Checks

```bash
npm run build
npm test
npm run test:e2e
```

Playwright browsers must be installed once before running the end-to-end tests:

```bash
npx playwright install chromium
```

The interface displays its shared connection and retry states when the API is unavailable. The backend must supply the authenticated user identity alongside its JWT login response.
