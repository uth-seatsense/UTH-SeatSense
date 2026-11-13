from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "status IN ('booked', 'checked_in', 'completed', 'cancelled', 'no_show')",
            name="ck_bookings_status",
        ),
        Index("idx_bookings_room_start", "room_id", "start_time"),
        Index("idx_bookings_user", "user_id"),
        Index(
            "idx_bookings_status",
            "status",
            postgresql_where=text("status IN ('booked', 'checked_in')"),
        ),
        # TC-07: Active bookings cannot overlap in the same room.
        ExcludeConstraint(
            ("room_id", "="),
            (text("tstzrange(start_time, end_time)"), "&&"),
            where=text("status IN ('booked', 'checked_in')"),
            using="gist",
            name="no_overlapping_bookings",
        ),
    )

    booking_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'booked'")
    )
    checkin_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
