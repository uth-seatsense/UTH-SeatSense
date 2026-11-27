from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.booking import Booking
from app.models.check_in import CheckIn
from app.models.checkin_token import CheckInToken
from app.services.booking_service import BookingError, _utc


class CheckInService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def issue_token(
        self,
        db: Session,
        *,
        user_id: int,
        booking_id: int,
        now: datetime | None = None,
    ) -> tuple[str, datetime, datetime]:
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
            raise BookingError("booking_not_active", "This booking is not active", 409)

        valid_from = _utc(booking.start_time)
        expires_at = valid_from + timedelta(minutes=self.settings.checkin_grace_minutes)
        if current_time >= expires_at:
            booking.status = "no_show"
            booking.no_show_at = current_time
            db.commit()
            raise BookingError("checkin_window_closed", "The check-in window is closed", 409)

        active_tokens = db.scalars(
            select(CheckInToken).where(
                CheckInToken.booking_id == booking_id,
                CheckInToken.used_at.is_(None),
                CheckInToken.revoked_at.is_(None),
            )
        ).all()
        for token in active_tokens:
            token.revoked_at = current_time

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        db.add(
            CheckInToken(
                booking_id=booking_id,
                token_hash=token_hash,
                created_at=current_time,
                expires_at=expires_at,
            )
        )
        db.commit()
        return raw_token, valid_from, expires_at

    def check_in(
        self,
        db: Session,
        *,
        user_id: int,
        booking_id: int,
        qr_token: str,
        now: datetime | None = None,
    ) -> datetime:
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
            raise BookingError("booking_not_active", "This booking is not active", 409)

        starts_at = _utc(booking.start_time)
        expires_at = starts_at + timedelta(minutes=self.settings.checkin_grace_minutes)
        if current_time < starts_at:
            raise BookingError("checkin_window_not_open", "Check-in is not open yet", 409)
        if current_time >= expires_at:
            booking.status = "no_show"
            booking.no_show_at = current_time
            db.commit()
            raise BookingError("checkin_window_closed", "The check-in window is closed", 409)

        token_hash = hashlib.sha256(qr_token.encode("utf-8")).hexdigest()
        token = db.scalar(
            select(CheckInToken)
            .where(
                CheckInToken.booking_id == booking_id,
                CheckInToken.token_hash == token_hash,
                CheckInToken.used_at.is_(None),
                CheckInToken.revoked_at.is_(None),
                CheckInToken.expires_at > current_time,
            )
            .with_for_update()
        )
        if token is None:
            raise BookingError("invalid_qr_token", "The QR code is invalid or expired", 401)

        token.used_at = current_time
        booking.status = "checked_in"
        booking.checkin_at = current_time
        db.add(
            CheckIn(
                booking_id=booking_id,
                checkin_time=current_time,
                method="qr",
                status="success",
            )
        )
        db.commit()
        return current_time
