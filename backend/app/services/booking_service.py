from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.booking import Booking
from app.models.room import Room
from app.models.user import User
from app.schemas.booking import BookingCreate

ACTIVE_STATUSES = ("booked", "checked_in")


class BookingError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 409):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def mark_due_no_shows(
    db: Session, settings: Settings, *, now: datetime | None = None
) -> None:
    current_time = now or datetime.now(timezone.utc)
    due = db.scalars(
        select(Booking).where(
            Booking.status == "booked",
            Booking.start_time
            <= current_time - timedelta(minutes=settings.checkin_grace_minutes),
        )
    ).all()
    for booking in due:
        booking.status = "no_show"
        booking.no_show_at = current_time
    if due:
        db.commit()


class BookingService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def create(
        self,
        db: Session,
        *,
        user_id: int,
        request: BookingCreate,
        now: datetime | None = None,
    ) -> Booking:
        current_time = now or datetime.now(timezone.utc)
        starts_at = request.starts_at
        ends_at = request.ends_at
        duration = ends_at - starts_at

        if starts_at <= current_time:
            raise BookingError("invalid_booking_time", "Booking must start in the future", 422)
        if duration < timedelta(minutes=self.settings.booking_min_duration_minutes) or (
            duration > timedelta(minutes=self.settings.booking_max_duration_minutes)
        ):
            raise BookingError(
                "invalid_booking_duration",
                "Booking duration is outside the permitted range",
                422,
            )
        if starts_at > current_time + timedelta(days=self.settings.booking_max_advance_days):
            raise BookingError(
                "booking_advance_limit",
                "Booking must start within the permitted advance window",
                422,
            )

        user = db.scalar(
            select(User).where(User.user_id == user_id).with_for_update()
        )
        if user is None or not user.is_active:
            raise BookingError("account_inactive", "The account is not active", 403)

        room = db.scalar(
            select(Room)
            .where(
                Room.id == request.room_id,
                Room.is_active.is_(True),
                Room.status == "active",
            )
            .with_for_update()
        )
        if room is None:
            raise BookingError("room_not_found", "Room does not exist", 404)
        if room.room_type not in ("topic_room", "group_study_room"):
            raise BookingError("room_not_bookable", "This room cannot be booked", 409)
        if request.participant_count > room.capacity:
            raise BookingError(
                "participant_limit_exceeded",
                "The group size exceeds the room capacity",
                422,
            )

        mark_due_no_shows(db, self.settings, now=current_time)
        day_start = starts_at.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        daily_count = db.scalar(
            select(func.count())
            .select_from(Booking)
            .where(
                Booking.user_id == user_id,
                Booking.start_time >= day_start,
                Booking.start_time < day_end,
                Booking.status.in_(("booked", "checked_in", "completed")),
            )
        )
        if (daily_count or 0) >= self.settings.booking_max_per_day:
            raise BookingError(
                "daily_limit_exceeded",
                "The daily booking limit has been reached",
                409,
            )

        gap = timedelta(minutes=self.settings.booking_gap_minutes)
        conflict = db.scalar(
            select(Booking.booking_id)
            .where(
                Booking.room_id == room.id,
                Booking.status.in_(ACTIVE_STATUSES),
                Booking.start_time < ends_at + gap,
                Booking.end_time > starts_at - gap,
            )
            .limit(1)
        )
        if conflict is not None:
            raise BookingError(
                "booking_conflict",
                "This room is already booked during that time",
                409,
            )

        booking = Booking(
            user_id=user_id,
            room_id=room.id,
            start_time=starts_at,
            end_time=ends_at,
            participant_count=request.participant_count,
            status="booked",
        )
        db.add(booking)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            if "no_overlapping_bookings" in str(exc.orig):
                raise BookingError(
                    "booking_conflict",
                    "This room is already booked during that time",
                    409,
                ) from None
            raise
        db.refresh(booking)
        return booking

    def list_for_user(
        self,
        db: Session,
        *,
        user_id: int,
        limit: int,
        offset: int,
        now: datetime | None = None,
    ) -> tuple[list[Booking], int]:
        mark_due_no_shows(db, self.settings, now=now)
        query = select(Booking).where(Booking.user_id == user_id)
        total = db.scalar(
            select(func.count()).select_from(Booking).where(Booking.user_id == user_id)
        ) or 0
        items = db.scalars(
            query.order_by(Booking.start_time.desc(), Booking.booking_id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        return items, total

    def cancel(
        self,
        db: Session,
        *,
        user_id: int,
        booking_id: int,
        now: datetime | None = None,
    ) -> None:
        current_time = now or datetime.now(timezone.utc)
        booking = db.scalar(
            select(Booking)
            .where(Booking.booking_id == booking_id)
            .with_for_update()
        )
        if booking is None:
            raise BookingError("booking_not_found", "Booking does not exist", 404)
        if booking.user_id != user_id:
            raise BookingError("forbidden", "This booking belongs to another user", 403)
        if booking.status != "booked":
            raise BookingError("booking_not_active", "This booking cannot be cancelled", 409)
        if _utc(booking.start_time) - current_time < timedelta(
            minutes=self.settings.booking_cancel_cutoff_minutes
        ):
            raise BookingError(
                "booking_cancel_window_closed",
                "The booking can no longer be cancelled online",
                409,
            )
        booking.status = "cancelled"
        db.commit()
