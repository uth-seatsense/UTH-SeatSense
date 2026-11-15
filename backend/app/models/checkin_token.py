from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CheckInToken(Base):
    __tablename__ = "checkin_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_checkin_tokens_hash"),
        CheckConstraint("expires_at > created_at", name="ck_checkin_tokens_expiry"),
        Index("idx_checkin_tokens_booking", "booking_id", "expires_at"),
        Index(
            "uq_checkin_tokens_active_booking",
            "booking_id",
            unique=True,
            postgresql_where=text("used_at IS NULL AND revoked_at IS NULL"),
        ),
    )

    token_id: Mapped[int] = mapped_column(
        Integer, Identity(always=False), primary_key=True
    )
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
