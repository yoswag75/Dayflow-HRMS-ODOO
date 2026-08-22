# Dayflow — Backend

> FastAPI modular monolith powering the Dayflow HRMS.

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- [Ollama](https://ollama.ai/) (for chatbot module)

### Setup

```bash
# 1. Clone & navigate
git clone https://github.com/yoswag75/Dayflow-HRMS-ODOO.git
cd Dayflow-HRMS-ODOO/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database URL and config

# 5. Run database migrations
alembic upgrade head

# 6. Start the dev server
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up --build
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/dayflow` |
| `SECRET_KEY` | JWT signing key | *(required)* |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name for chatbot | `llama3` |
| `OLLAMA_TIMEOUT` | Request timeout (seconds) | `30` |
| `EMAIL_PROVIDER` | Email dispatch backend | `null` (options: `null`, `smtp`, `sendgrid`) |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, router registration
│   │
│   ├── core/                      # Cross-cutting concerns (DevOps-owned)
│   │   ├── config.py              # Pydantic Settings
│   │   ├── database.py            # SQLAlchemy engine, SessionLocal, Base
│   │   ├── security.py            # JWT auth, get_current_user
│   │   └── scheduler.py           # APScheduler daily jobs
│   │
│   ├── shared/
│   │   └── change_request/        # Shared approval/diff pattern
│   │       ├── models.py
│   │       ├── schemas.py
│   │       └── service.py
│   │
│   └── modules/
│       ├── auth/                  # Sign up/in, JWT tokens
│       │   ├── models.py          # User table
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       │
│       ├── employee/              # Profile CRUD, verified edits
│       ├── attendance/            # Check-in/out, streak tracking
│       ├── leave/                 # Time-off requests, emergency fast-track
│       ├── payroll/               # Salary components, 30-day change workflow
│       ├── onboarding/            # Checklists, buddy assignment
│       │
│       ├── gamification/          # Points, badges, leaderboard
│       │   ├── models.py          # PointsLedger, Badge, EmployeeBadge
│       │   ├── schemas.py
│       │   ├── rules.py           # Pure business rules (no DB)
│       │   ├── service.py
│       │   └── router.py
│       │
│       ├── simulation/            # What-if workforce scenarios
│       │   ├── models.py          # SimulationRun (audit log)
│       │   ├── schemas.py
│       │   ├── engine.py          # Pure deterministic calculations (no DB)
│       │   ├── service.py
│       │   └── router.py
│       │
│       ├── chatbot/               # Ollama-powered HR assistant
│       │   ├── models.py          # ChatSession, ChatMessage
│       │   ├── schemas.py
│       │   ├── ollama_client.py   # Streaming Ollama HTTP client
│       │   ├── service.py         # Context builder + message handler
│       │   └── router.py
│       │
│       └── notification/          # In-app + email notifications
│           ├── models.py          # Notification, NotificationPreference
│           ├── schemas.py         # NotificationCreate (public contract)
│           ├── providers.py       # EmailProvider interface (SMTP/SendGrid/Null)
│           ├── service.py
│           └── router.py
│
├── alembic/                       # Database migrations
├── tests/
│   ├── stubs/
│   │   └── schemas.py             # Mock Pydantic schemas for cross-module dev
│   └── seeds/                     # Seed data for testing
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## Module Dependency Map

```
core/ (DevOps)
  └── Dev A modules (employee, attendance, leave, payroll, onboarding, shared/change_request)
        └── Dev B modules (notification → gamification → simulation → chatbot)
```

**Key rule:** Dev B modules consume Dev A modules via **Pydantic schemas and service functions only** — never import SQLAlchemy models directly.

---

## API Endpoints (Dev B Modules)

### Notification (`/notifications`)
| Method | Path | Description |
|---|---|---|
| `GET` | `/notifications/me` | List current user's notifications |
| `POST` | `/notifications/{id}/read` | Mark a notification as read |
| `GET` | `/notifications/preferences` | Get notification preferences |
| `PUT` | `/notifications/preferences` | Update notification preferences |

### Gamification (`/gamification`)
| Method | Path | Description |
|---|---|---|
| `GET` | `/gamification/leaderboard` | Points leaderboard (filterable by department/period) |
| `GET` | `/gamification/me/points` | Current user's points history |
| `GET` | `/gamification/me/badges` | Current user's earned badges |

### Simulation (`/simulation`)
| Method | Path | Description |
|---|---|---|
| `POST` | `/simulation/run` | Run a what-if scenario |
| `GET` | `/simulation/history/{user_id}` | Simulation run history |

### Chatbot (`/chatbot`)
| Method | Path | Description |
|---|---|---|
| `POST` | `/chatbot/session` | Create a new chat session |
| `POST` | `/chatbot/message` | Send a message (streaming response) |
| `GET` | `/chatbot/session/{id}/history` | Get chat session history |

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific module tests
pytest tests/test_gamification.py
pytest tests/test_simulation.py
pytest tests/test_chatbot.py
pytest tests/test_notification.py
```

### Test Strategy

| Layer | Approach |
|---|---|
| Pure functions (`rules.py`, `engine.py`) | Unit tests, no DB fixture |
| Service layer | pytest-mock for cross-module dependencies |
| Router / API | FastAPI `TestClient` |
| Integration | pytest-asyncio + real SQLite |
| Cross-module | Badge award → notification trigger |

---

## License

This project is part of the Dayflow HRMS system.
