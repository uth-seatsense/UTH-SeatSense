from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CountingSession(Base):
    __tablename__ = "counting_sessions"
    __table_args__ = (
        CheckConstraint("initial_count >= 0", name="ck_counting_sessions_initial_count"),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at", name="ck_counting_sessions_end"
        ),
        Index(
            "uq_counting_sessions_active_room",
            "room_id",
            unique=True,
            postgresql_where=text("ended_at IS NULL"),
            sqlite_where=text("ended_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    room_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
