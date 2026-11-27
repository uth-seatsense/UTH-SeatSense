from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Path, status
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictInt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.api.errors import api_error
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.user import User
from app.schemas.cv_count import ErrorEnvelope
from app.schemas.occupancy import (
    MAX_CURRENT_COUNT,
    MAX_ROOM_ID,
    CurrentOccupancyResponse,
)
from app.services.cv_count_service import CVCountService, OccupancyNotFoundError
from app.services.occupancy_service import OccupancyService, RoomNotFoundError


router = APIRouter()
cv_count_service = CVCountService()
RoomDataStatus = Literal["fresh", "stale", "offline", "insufficient"]


class CountingSessionStart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    initial_count: StrictInt = Field(ge=0, le=MAX_CURRENT_COUNT)


class CountingSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    initial_count: int
    started_at: AwareDatetime
    started_by: int


class RoomOccupancyStatus(BaseModel):
    room_id: int
    room_code: str
    room_name: str
    campus_code: str | None = None
    campus_name: str | None = None
    capacity: int
    capacity_confirmed: bool
    current_count: int | None
    available_seats: int | None
    over_capacity: bool | None
    updated_at: datetime | None
    is_stale: bool
    occupancy_status: RoomDataStatus


class RoomOccupancyStatusResponse(BaseModel):
    rooms: list[RoomOccupancyStatus]
    total_rooms: int
    web_logged_in_count: int
    total_people_in_rooms: int | None
    updated_at: datetime | None


class RoomOccupancyDetail(BaseModel):
    room_id: int
    room_code: str
    camera_id: str | None
    source_type: Literal["webcam"]
    people_count: int | None
    tracked_count: int | None
    estimated_occupancy: int | None
    available_seats: int | None
    over_capacity: bool | None
    occupancy_underflow: bool | None
    recorded_at: AwareDatetime | None
    received_at: AwareDatetime | None
    is_stale: bool
    occupancy_status: RoomDataStatus


class CurrentSessionOccupancy(CurrentOccupancyResponse):
    data_status: Literal["fresh", "stale", "disconnected", "insufficient"] | None = None


@router.post(
    "/rooms/{room_id}/counting-sessions",
    response_model=CountingSessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Start a counting session with a manual headcount",
)
#seat 73
def start_counting_session(
    payload: CountingSessionStart,
    room_id: int = Path(gt=0, le=MAX_ROOM_ID),
    user: User = Depends(require_roles("librarian", "admin")),
    db: Session = Depends(get_db),
) -> CountingSessionRead:
    try:
        session = OccupancyService.start_counting_session(
            db, room_id, payload.initial_count, user.user_id
        )
    except RoomNotFoundError:
        raise api_error(404, "room_not_found", "Active room does not exist") from None
    return CountingSessionRead.model_validate(session)


def _room_data_status(updated_at: datetime | None) -> RoomDataStatus:
    data_status = OccupancyService.calculate_data_status(updated_at)
    if data_status is None:
        return "insufficient"
    if data_status == "disconnected":
        return "offline"
    return data_status


@router.get(
    "/rooms/{room_id}/latest",
    response_model=RoomOccupancyDetail,
    responses={
        404: {"model": ErrorEnvelope, "description": "Room not found"},
        422: {"model": ErrorEnvelope, "description": "Invalid room ID"},
        503: {"model": ErrorEnvelope, "description": "Database unavailable"},
    },
)
def read_latest_occupancy(
    room_id: int = Path(gt=0, le=MAX_ROOM_ID),
    db: Session = Depends(get_db),
) -> RoomOccupancyDetail:
    rooms = OccupancyService.current_room_counts(db, room_id=room_id)
    if not rooms:
        raise api_error(404, "room_not_found", "Active room does not exist")

    room = rooms[0]
    data_status = _room_data_status(room["updated_at"])
    snapshot = None
    if room["current_count"] is not None:
        try:
            snapshot = cv_count_service.latest_live_for_room(db, room_id)
        except OccupancyNotFoundError:
            pass

    return RoomOccupancyDetail(
        room_id=room_id,
        room_code=room["room_code"],
        camera_id=snapshot.camera_id if snapshot else None,
        source_type="webcam",
        people_count=snapshot.people_count if snapshot else None,
        tracked_count=snapshot.tracked_count if snapshot else None,
        estimated_occupancy=room["current_count"],
        available_seats=room["available_seats"],
        over_capacity=room["over_capacity"],
        occupancy_underflow=room["underflow"],
        recorded_at=room["observed_at"],
        received_at=room["updated_at"],
        is_stale=data_status in {"stale", "offline"},
        occupancy_status=data_status,
    )


def _web_logged_in_count(db: Session) -> int:
    return db.scalar(
        select(func.count(func.distinct(AuthSession.user_id))).where(
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > datetime.now(timezone.utc),
        )
    )


@router.get("/current", response_model=CurrentSessionOccupancy)
def get_current_occupancy(
    db: Session = Depends(get_db),
    campus: str | None = None,
) -> CurrentSessionOccupancy:
    rooms = get_room_occupancy_status(db, campus)
    location = "Thư viện UTH"
    if campus is not None:
        location = next(
            (room.campus_name for room in rooms.rooms if room.campus_name), location
        )
    data_status = "insufficient"
    if rooms.total_people_in_rooms is not None:
        data_status = OccupancyService.calculate_data_status(rooms.updated_at)
    return CurrentSessionOccupancy(
        current_count=rooms.total_people_in_rooms,
        updated_at=rooms.updated_at,
        location=location,
        web_logged_in_count=rooms.web_logged_in_count,
        active_room_count=sum(room.current_count is not None for room in rooms.rooms),
        data_status=data_status,
    )


@router.get("/rooms/status", response_model=RoomOccupancyStatusResponse)
def get_room_occupancy_status(
    db: Session = Depends(get_db),
    campus: str | None = None,
) -> RoomOccupancyStatusResponse:
    rooms = []
    for row in OccupancyService.current_room_counts(db, campus=campus):
        data_status = _room_data_status(row["updated_at"])
        rooms.append(
            RoomOccupancyStatus(
                **row,
                is_stale=data_status in {"stale", "offline"},
                occupancy_status=data_status,
            )
        )

    counts = [room.current_count for room in rooms if room.current_count is not None]
    return RoomOccupancyStatusResponse(
        rooms=rooms,
        total_rooms=len(rooms),
        web_logged_in_count=_web_logged_in_count(db),
        total_people_in_rooms=sum(counts) if rooms and len(counts) == len(rooms) else None,
        updated_at=max(
            (room.updated_at for room in rooms if room.updated_at is not None),
            default=None,
        ),
    )
