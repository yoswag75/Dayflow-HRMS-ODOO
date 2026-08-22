# Dayflow frontend

A responsive React prototype for the HR management system. The current build uses an in-memory service layer so the complete interface can be reviewed before connecting it to the backend API.

## Run locally

```bash
npm install
npm run dev
```

Vite serves the application at `http://localhost:5173` by default.

## Demo accounts

| Role | Employee ID | Password |
| --- | --- | --- |
| HR administrator | `HRDEMO001` | `Dayflow123!` |
| Employee | `EMPDEMO001` | `Dayflow123!` |
| First-login employee | `NEWEMP001` | `Dayflow123!` |

The first-login account demonstrates the mandatory password-change flow.

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

## Mock error state

Set `dayflow:force-error` to `true` in browser session storage to force mock API failures and review the shared retry interface.
