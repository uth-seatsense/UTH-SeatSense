from fastapi import APIRouter

from app.api.v1.endpoints import (
    checkin,
    dashboard,
    occupancy,
    reservations,
    rooms,
)

api_router = APIRouter()
api_router.include_router(occupancy.router, prefix="/occupancy", tags=["occupancy"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(
    reservations.router, prefix="/reservations", tags=["reservations"]
)
api_router.include_router(checkin.router, prefix="/checkin", tags=["check-in"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
