from fastapi import APIRouter, Depends, Path
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.api.errors import api_error
from app.db.session import get_db
from app.schemas.cv_count import ErrorEnvelope, LatestRoomOccupancy
from app.schemas.occupancy import CurrentOccupancyResponse
from app.services.cv_count_service import (
    CVCountService,
    OccupancyNotFoundError,
    RoomNotFoundError,
    is_stale,
)

router = APIRouter()
cv_count_service = CVCountService()
MAX_ROOM_ID = 2**63 - 1


class RoomOccupancyStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    room_id: int
    room_code: str
    room_name: str
    campus_code: str | None = None
    campus_name: str | None = None
    capacity: int
    capacity_confirmed: bool
    current_count: int | None
    available_seats: int | None
    updated_at: datetime | None
    is_stale: bool


class RoomOccupancyStatusResponse(BaseModel):
    rooms: list[RoomOccupancyStatus]
    total_rooms: int
    web_logged_in_count: int
    total_people_in_rooms: int
    updated_at: datetime | None


@router.get(
    "/rooms/{room_id}/latest",
    response_model=LatestRoomOccupancy,
    responses={
        404: {"model": ErrorEnvelope, "description": "Room/data not found"},
        422: {"model": ErrorEnvelope, "description": "Invalid room ID"},
        503: {"model": ErrorEnvelope, "description": "Database unavailable"},
    },
)
def read_latest_occupancy(
    room_id: int = Path(gt=0, le=MAX_ROOM_ID),
    db: Session = Depends(get_db),
) -> LatestRoomOccupancy:
    try:
        record = cv_count_service.latest_live_for_room(db, room_id)
    except RoomNotFoundError:
        raise api_error(404, "room_not_found", "Room does not exist") from None
    except OccupancyNotFoundError:
        raise api_error(
            404,
            "occupancy_not_found",
            "No live occupancy record is available for this room",
        ) from None
    except SQLAlchemyError:
        raise api_error(
            503,
            "database_unavailable",
            "The database is temporarily unavailable",
        ) from None

    return LatestRoomOccupancy(
        room_id=record.room_id,
        room_code=record.room_code,
        camera_id=record.camera_id,
        source_type="webcam",
        people_count=record.people_count,
        tracked_count=record.tracked_count,
        estimated_occupancy=record.estimated_occupancy,
        occupancy_underflow=record.occupancy_underflow,
        recorded_at=record.recorded_at,
        received_at=record.received_at,
        is_stale=is_stale(record.received_at),
    )


@router.get("/current", response_model=CurrentOccupancyResponse)
def get_current_occupancy(
    db: Session = Depends(get_db),
    campus: str | None = None,
) -> CurrentOccupancyResponse:
    query = text(
            """
            SELECT
                CASE WHEN COUNT(*) = 0 THEN NULL ELSE SUM(current_count)::INTEGER END AS current_count,
                MAX(updated_at) AS updated_at,
                COALESCE(MAX(campus_name), 'Thư viện UTH') AS location,
                (SELECT COUNT(DISTINCT user_id)
                   FROM auth_sessions
                  WHERE revoked_at IS NULL
                    AND expires_at > NOW()) AS web_logged_in_count,
                COUNT(*) AS active_room_count
            FROM room_occupancy_status
            WHERE (:campus IS NULL OR campus_code = :campus)
            """
        ).bindparams(campus=campus)
    result = db.execute(query).mappings().one()
    return CurrentOccupancyResponse(**result)


@router.get("/rooms/status", response_model=RoomOccupancyStatusResponse)
def get_room_occupancy_status(
    db: Session = Depends(get_db),
    campus: str | None = None,
) -> RoomOccupancyStatusResponse:
    query = text(
            """
            SELECT room_id, room_code, room_name, campus_code, campus_name,
                   capacity, capacity_confirmed, current_count,
                   available_seats, updated_at
            FROM room_occupancy_status
            WHERE (:campus IS NULL OR campus_code = :campus)
            ORDER BY room_id
            """
        ).bindparams(campus=campus)
    rows = db.execute(query).mappings().all()

    web_count = db.execute(
        text(
            """
            SELECT COUNT(DISTINCT user_id) AS web_logged_in_count
            FROM auth_sessions
            WHERE revoked_at IS NULL AND expires_at > NOW()
            """
        )
    ).mappings().one()["web_logged_in_count"]

    now = datetime.now(timezone.utc)
    rooms = []
    for row in rows:
        updated_at = row["updated_at"]
        if updated_at is not None and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        is_stale = updated_at is None or now - updated_at > timedelta(seconds=30)
        rooms.append(
            RoomOccupancyStatus(
                room_id=row["room_id"],
                room_code=row["room_code"],
                room_name=row["room_name"],
                campus_code=row["campus_code"],
                campus_name=row["campus_name"],
                capacity=row["capacity"],
                capacity_confirmed=row["capacity_confirmed"],
                current_count=row["current_count"],
                available_seats=row["available_seats"],
                updated_at=updated_at,
                is_stale=is_stale,
            )
        )

    return RoomOccupancyStatusResponse(
        rooms=rooms,
        total_rooms=len(rooms),
        web_logged_in_count=int(web_count),
        total_people_in_rooms=sum(
            room.current_count or 0 for room in rooms
        ),
        updated_at=max(
            (room.updated_at for room in rooms if room.updated_at is not None),
            default=None,
        ),
    )
