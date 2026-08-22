from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from app.core.database import Base, engine
from app.modules.auth.router import router as auth_router
from app.modules.employee.router import router as employee_router
from app.modules.attendance.router import router as attendance_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.leave.router import router as leave_router
from app.modules.payroll.router import router as payroll_router
from app.modules.notification.router import router as notification_router
from app.modules.gamification.router import router as gamification_router
from app.modules.simulation.router import router as simulation_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dayflow HRMS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(onboarding_router)
app.include_router(leave_router)
app.include_router(payroll_router)
app.include_router(notification_router)
app.include_router(gamification_router)
app.include_router(simulation_router)
=======
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

>>>>>>> d80e6553fe1ed5dffcdd64aed8f583c84f9cd895


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
