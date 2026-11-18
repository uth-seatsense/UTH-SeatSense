from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import api_error
from app.db.session import get_db
from app.models.campus import Campus
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomListResponse, RoomRead

router = APIRouter()


def _room_type(room_type: str) -> str:
    return {
        "reading_room": "free_area",
        "group_study_room": "topic_room",
    }.get(room_type, room_type)


def _room_read(room: Room, campus_code: str | None) -> RoomRead:
    return RoomRead(
        id=room.id,
        code=room.code,
        name=room.name,
        room_type=_room_type(room.room_type),
        capacity=room.capacity,
        campus_code=campus_code,
        building=room.building,
        location=room.location,
        is_active=room.is_active and room.status == "active",
    )


@router.get("", response_model=RoomListResponse)
def list_rooms(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    campus_code: str | None = Query(default=None, pattern=r"^(CS1|CS3)$"),
    room_type: str | None = Query(default=None, pattern=r"^(free_area|topic_room)$"),
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoomListResponse:
    query = (
        select(Room, Campus.code)
        .outerjoin(Campus, Campus.campus_id == Room.campus_id)
        .where(Room.is_active.is_(True), Room.status == "active")
    )
    count_query = (
        select(func.count())
        .select_from(Room)
        .outerjoin(Campus, Campus.campus_id == Room.campus_id)
        .where(Room.is_active.is_(True), Room.status == "active")
    )
    if campus_code is not None:
        query = query.where(Campus.code == campus_code)
        count_query = count_query.where(Campus.code == campus_code)
    if room_type is not None:
        legacy_types = {
            "free_area": ("free_area", "reading_room"),
            "topic_room": ("topic_room", "group_study_room"),
        }[room_type]
        query = query.where(Room.room_type.in_(legacy_types))
        count_query = count_query.where(Room.room_type.in_(legacy_types))

    total = db.scalar(count_query) or 0
    rows = db.execute(
        query.order_by(Room.id).limit(limit).offset(offset)
    ).all()
    return RoomListResponse(
        items=[_room_read(room, code) for room, code in rows],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.get("/{room_id}", response_model=RoomRead)
def get_room(
    room_id: int = Path(gt=0),
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoomRead:
    row = db.execute(
        select(Room, Campus.code)
        .outerjoin(Campus, Campus.campus_id == Room.campus_id)
        .where(
            Room.id == room_id,
            Room.is_active.is_(True),
            Room.status == "active",
        )
    ).one_or_none()
    if row is None:
        raise api_error(404, "room_not_found", "Room does not exist")
    room, campus_code = row
    return _room_read(room, campus_code)
