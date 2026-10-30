from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import get_session_factory

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get('/health/db', tags=['health'])
def database_health():
    try:
        with get_session_factory()() as session:
            session.execute(text('SELECT 1'))
    except (SQLAlchemyError,ValueError):
        raise HTTPException(503, 'Database unavailable')
    return {'status':'ok','database':'postgresql'}
