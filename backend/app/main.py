from fastapi import FastAPI
from sqlalchemy import text

from app.webhooks.routes import router as webhook_router
from app.core.config import get_settings
from app.db.session import engine
from app.api.routes import router as api_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered revenue recovery decision engine.",
)

app.include_router(webhook_router)
app.include_router(api_router)

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