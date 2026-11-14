from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CheckIn(Base):
    __tablename__ = "check_ins"
    __table_args__ = (
        Index("idx_checkins_booking", "booking_id"),
        Index("idx_checkins_time", "checkin_time"),
    )

    checkin_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    checkin_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    method: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'qr'")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'success'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
