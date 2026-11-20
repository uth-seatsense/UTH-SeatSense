from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CountEvent(Base):
    __tablename__ = "count_events"
    __table_args__ = (
        Index("idx_count_events_room", "room_id", "event_time", postgresql_using="btree"),
        Index("idx_count_events_received", "received_at", postgresql_using="btree"),
    )

    event_id: Mapped[object] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    session_id: Mapped[object] = mapped_column(Uuid(as_uuid=True), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    device_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="online", server_default=text("'online'")
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="cv", server_default=text("'cv'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
