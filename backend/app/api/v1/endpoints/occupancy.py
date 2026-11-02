from fastapi import APIRouter, Depends, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.errors import api_error
from app.db.session import get_db
from app.schemas.cv_count import ErrorEnvelope, LatestRoomOccupancy
from app.services.cv_count_service import (
    CVCountService,
    OccupancyNotFoundError,
    RoomNotFoundError,
    is_stale,
)

router = APIRouter()
cv_count_service = CVCountService()
MAX_ROOM_ID = 2**63 - 1


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
