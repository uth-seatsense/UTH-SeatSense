from fastapi import APIRouter

from app.api import auth
from app.api.v1.endpoints import (
    bookings,
    checkin,
    cv,
    dashboard,
    occupancy,
    rooms,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
api_router.include_router(occupancy.router, prefix="/occupancy", tags=["occupancy"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(checkin.router, prefix="/check-in", tags=["check-in"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
