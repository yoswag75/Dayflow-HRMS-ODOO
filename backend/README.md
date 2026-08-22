# Dayflow HRMS - Backend

Dayflow HRMS core backend services built with FastAPI, SQLAlchemy, and PostgreSQL/SQLite.

## Quick Start

### 1. Local Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Docker Setup (Optional)

```bash
docker compose up -d
```
