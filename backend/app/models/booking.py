from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import TSTZRANGE, ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "participant_count IS NULL OR participant_count BETWEEN 2 AND 6",
            name="ck_bookings_participant_count",
        ),
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
        # TC-07: Prevent overlapping bookings
        # Note: ExcludeConstraint requires btree_gist extension
        # The actual constraint is created in migration SQL
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
    # Existing rows remain nullable until migrated data is reviewed; new booking
    # requests must supply a value and the API validates the SRS range 2..6.
    participant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checkin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    no_show_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'booked'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
