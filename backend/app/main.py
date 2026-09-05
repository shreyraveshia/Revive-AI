from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered revenue recovery decision engine.",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/health/db")
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar_one()

    return {
        "status": "ok",
        "database": "connected",
        "result": str(value),
    }