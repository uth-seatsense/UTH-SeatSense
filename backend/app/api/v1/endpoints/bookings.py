from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import api_error
from app.core.config import settings
from app.db.session import get_db
from app.models.booking import Booking
from app.models.campus import Campus
from app.models.room import Room
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingListResponse, BookingRead
from app.schemas.checkin import CheckInTokenRead
from app.schemas.room import RoomRead
from app.services.booking_service import BookingError, BookingService
from app.services.checkin_service import CheckInService

router = APIRouter()


def _booking_read(db: Session, booking: Booking) -> BookingRead:
    room = db.get(Room, booking.room_id)
    if room is None:
        raise api_error(404, "room_not_found", "Room does not exist")
    campus = db.get(Campus, room.campus_id) if room.campus_id is not None else None
    room_type = {
        "reading_room": "free_area",
        "group_study_room": "topic_room",
    }.get(room.room_type, room.room_type)
    return BookingRead(
        id=booking.booking_id,
        room_id=booking.room_id,
        user_id=booking.user_id,
        participant_count=booking.participant_count,
        status=booking.status,
        starts_at=booking.start_time,
        ends_at=booking.end_time,
        checkin_at=booking.checkin_at,
        no_show_at=booking.no_show_at,
        room=RoomRead(
            id=room.id,
            code=room.code,
            name=room.name,
            room_type=room_type,
            capacity=room.capacity,
            campus_code=campus.code if campus else None,
            building=room.building,
            location=room.location,
            is_active=room.is_active and room.status == "active",
        ),
    )


def _raise_booking_error(error: BookingError) -> None:
    raise api_error(error.status_code, error.code, error.message) from None


@router.get("", response_model=BookingListResponse)
def list_bookings(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingListResponse:
    bookings, total = BookingService(settings).list_for_user(
        db, user_id=user.user_id, limit=limit, offset=offset
    )
    return BookingListResponse(
        items=[_booking_read(db, booking) for booking in bookings],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingRead:
    try:
        booking = BookingService(settings).create(
            db, user_id=user.user_id, request=payload
        )
    except BookingError as error:
        _raise_booking_error(error)
    return _booking_read(db, booking)


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(
    booking_id: int = Path(gt=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingRead:
    booking = db.scalar(
        select(Booking).where(
            Booking.booking_id == booking_id,
            Booking.user_id == user.user_id,
        )
    )
    if booking is None:
        raise api_error(404, "booking_not_found", "Booking does not exist")
    return _booking_read(db, booking)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int = Path(gt=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    try:
        BookingService(settings).cancel(
            db, user_id=user.user_id, booking_id=booking_id
        )
    except BookingError as error:
        _raise_booking_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{booking_id}/check-in-token",
    response_model=CheckInTokenRead,
    status_code=status.HTTP_201_CREATED,
)
def create_checkin_token(
    booking_id: int = Path(gt=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckInTokenRead:
    try:
        token, valid_from, expires_at = CheckInService(settings).issue_token(
            db, user_id=user.user_id, booking_id=booking_id
        )
    except BookingError as error:
        _raise_booking_error(error)
    return CheckInTokenRead(
        booking_id=booking_id,
        qr_token=token,
        valid_from=valid_from,
        expires_at=expires_at,
    )
