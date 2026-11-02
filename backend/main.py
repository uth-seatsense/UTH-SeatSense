from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import get_session_factory

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/api/v1")


def _field_path(location: tuple[object, ...], issue: str = "") -> str:
    parts: list[str] = []
    for item in location:
        if item in {"body", "query", "path", "header", "cookie"}:
            continue
        if isinstance(item, int) and parts:
            parts[-1] = f"{parts[-1]}[{item}]"
        elif isinstance(item, str):
            parts.append(item)

    path = ".".join(parts) or "request"
    if parts and parts[-1].endswith("]"):
        if "tracked_count" in issue:
            return f"{path}.tracked_count"
        if "line_enabled" in issue or "line counting" in issue:
            return f"{path}.line_enabled"
        if "estimated_occupancy" in issue:
            return f"{path}.estimated_occupancy"
        if "occupancy_underflow" in issue:
            return f"{path}.occupancy_underflow"
    return path


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error})


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    if any(error.get("type") == "json_invalid" for error in errors):
        return _error_response(400, "malformed_json", "Request body is not valid JSON")

    details = [
        {
            "field": _field_path(tuple(error.get("loc", ())), error.get("msg", "")),
            "issue": str(error.get("msg", "Invalid value")),
        }
        for error in errors
    ]
    message = (
        "One or more CV records are invalid"
        if request.url.path == "/api/v1/cv/count-records"
        else "Request validation failed"
    )
    return _error_response(
        422,
        "validation_error",
        message,
        details,
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
            headers=exc.headers,
        )
    code = "not_found" if exc.status_code == 404 else "http_error"
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(exc.status_code, code, message)


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(
    _request: Request, _exc: SQLAlchemyError
) -> JSONResponse:
    return _error_response(
        503,
        "database_unavailable",
        "The database is temporarily unavailable",
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    _request: Request, _exc: Exception
) -> JSONResponse:
    return _error_response(500, "internal_error", "An unexpected error occurred")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@app.get("/health/db", tags=["health"])
def database_health() -> dict[str, str]:
    try:
        with get_session_factory()() as session:
            session.execute(text("SELECT 1"))
    except (SQLAlchemyError, ValueError):
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "database_unavailable",
                    "message": "The database is temporarily unavailable",
                }
            },
        )
    return {"status": "ok", "database": "postgresql"}
