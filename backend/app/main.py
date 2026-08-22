from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine

# Import models so SQLAlchemy registers all tables
from app.modules.auth import models as auth_models
from app.modules.notification import models as notification_models
from app.modules.gamification import models as gamification_models
from app.modules.simulation import models as simulation_models

from app.modules.notification.router import router as notification_router
from app.modules.gamification.router import router as gamification_router
from app.modules.simulation.router import router as simulation_router


# Create database tables
Base.metadata.create_all(bind=engine)


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


app.include_router(notification_router)
app.include_router(gamification_router)
app.include_router(simulation_router)


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