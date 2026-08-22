from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, get_db
from app.modules.notification.router import router as notification_router
from app.modules.gamification.router import router as gamification_router
import sqlite3
from sqlalchemy import create_engine

# Just for local testing until DevOps sets up PostgreSQL
engine = create_engine("sqlite:///./dayflow.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dayflow HRMS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers we have so far
app.include_router(notification_router)
app.include_router(gamification_router)

@app.get("/")
def root():
    return {"message": "Welcome to Dayflow HRMS API"}
