from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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
    record = None
    try:
        record = cv_count_service.latest_live_for_room(db, room_id)
    except RoomNotFoundError:
        raise api_error(404, "room_not_found", "Room does not exist") from None
    except OccupancyNotFoundError:
        record = None
    except SQLAlchemyError:
        raise api_error(
            503,
            "database_unavailable",
            "The database is temporarily unavailable",
        ) from None

    if record is None:
        legacy = db.execute(
            text(
                """
                SELECT rooms.code AS room_code,
                       occupancy.current_count,
                       occupancy.recorded_at
                FROM occupancy_records AS occupancy
                JOIN rooms ON rooms.id = occupancy.room_id
                WHERE occupancy.room_id = :room_id
                ORDER BY occupancy.recorded_at DESC, occupancy.id DESC
                LIMIT 1
                """
            ),
            {"room_id": room_id},
        ).mappings().one_or_none()
        if legacy is None:
            raise api_error(
                404,
                "occupancy_not_found",
                "No live occupancy record is available for this room",
            ) from None
        recorded_at = legacy["recorded_at"]
        count = legacy["current_count"]
        return LatestRoomOccupancy(
            room_id=room_id,
            room_code=legacy["room_code"],
            camera_id="legacy-occupancy",
            source_type="webcam",
            people_count=count,
            tracked_count=count,
            estimated_occupancy=count,
            occupancy_underflow=False,
            recorded_at=recorded_at,
            received_at=recorded_at,
            is_stale=is_stale(recorded_at),
        )

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
    campus_code: str | None = Query(default=None, pattern=r"^(CS1|CS3)$"),
) -> CurrentOccupancyResponse:
    occupancy_columns = set(
        db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'occupancy_records'
                """
            )
        ).scalars()
    )
    if "current_count" in occupancy_columns:
        legacy_count_column = "occupancy.current_count"
        legacy_time_column = "occupancy.recorded_at"
    else:
        legacy_count_column = "occupancy.occupied_count"
        legacy_time_column = "occupancy.observed_at"

    campus_filter = (
        ""
        if campus_code is None
        else f"AND campuses.code = '{campus_code}'"
    )
    result = db.execute(
        text(
            f"""
            WITH latest_cv_per_room AS (
                SELECT DISTINCT ON (occupancy.room_id)
                    occupancy.room_id,
                    occupancy.estimated_occupancy,
                    occupancy.recorded_at
                FROM cv_count_records AS occupancy
                JOIN rooms ON rooms.id = occupancy.room_id
                LEFT JOIN campuses ON campuses.campus_id = rooms.campus_id
                WHERE rooms.is_active IS TRUE
                  AND occupancy.estimated_occupancy IS NOT NULL
                  {campus_filter}
                ORDER BY occupancy.room_id, occupancy.recorded_at DESC, occupancy.id DESC
            ),
            latest_legacy_per_room AS (
                SELECT DISTINCT ON (occupancy.room_id)
                    occupancy.room_id,
                    {legacy_count_column} AS current_count,
                    {legacy_time_column} AS recorded_at
                FROM occupancy_records AS occupancy
                JOIN rooms ON rooms.id = occupancy.room_id
                LEFT JOIN campuses ON campuses.campus_id = rooms.campus_id
                WHERE rooms.is_active IS TRUE
                  {campus_filter}
                ORDER BY occupancy.room_id, {legacy_time_column} DESC, occupancy.id DESC
            ),
            latest_per_room AS (
                SELECT
                    rooms.id AS room_id,
                    COALESCE(cv.estimated_occupancy, legacy.current_count) AS current_count,
                    GREATEST(cv.recorded_at, legacy.recorded_at) AS updated_at
                FROM rooms
                LEFT JOIN latest_cv_per_room AS cv ON cv.room_id = rooms.id
                LEFT JOIN latest_legacy_per_room AS legacy ON legacy.room_id = rooms.id
                LEFT JOIN campuses ON campuses.campus_id = rooms.campus_id
                WHERE rooms.is_active IS TRUE
                  {campus_filter}
                  AND (cv.room_id IS NOT NULL OR legacy.room_id IS NOT NULL)
            )
            SELECT
                CASE
                    WHEN COUNT(*) = 0 THEN NULL
                    ELSE SUM(current_count)::INTEGER
                END AS current_count,
                MAX(updated_at) AS updated_at,
                'Thư viện UTH' AS location
            FROM latest_per_room
            """
        )
    ).mappings().one()
    return CurrentOccupancyResponse(**result)
