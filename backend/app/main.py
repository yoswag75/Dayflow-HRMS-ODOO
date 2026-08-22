from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.modules.attendance.router import router as attendance_router
from app.modules.auth.router import router as auth_router
from app.modules.chatbot.router import router as chatbot_router
from app.modules.employee.router import router as employee_router
from app.modules.gamification.router import router as gamification_router
from app.modules.leave.router import router as leave_router
from app.modules.notification.router import router as notification_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.payroll.router import router as payroll_router
from app.modules.simulation.router import router as simulation_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth_router,
    employee_router,
    attendance_router,
    onboarding_router,
    leave_router,
    payroll_router,
    notification_router,
    gamification_router,
    simulation_router,
    chatbot_router,
):
    app.include_router(router)


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API", "version": settings.VERSION, "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
