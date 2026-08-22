# Dayflow frontend

A responsive React frontend for the HR management system. All application data is loaded from the backend API; there is no production mock-data fallback.

## Run locally

```bash
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
