from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.models import TwinProfile
from app.routers import profile_router
from app.routers import simulate
from app.routers import scenario

settings = get_settings()

# Suitable for the hackathon prototype.
# Alembic migrations should be used later for production.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for financial profiles and what-if simulations",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router)
app.include_router(simulate.router)
app.include_router(scenario.router)

@app.get("/")
def root():
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "financial-digital-twin-api",
        "environment": settings.environment,
    }