from datetime import datetime
from uuid import UUID
from sqlalchemy import BigInteger, Integer, String, Boolean, Float, DateTime, ForeignKey, Identity, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.room import Room  # register FK target in metadata


class CVCountRecord(Base):
    __tablename__ = 'cv_count_records'
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    schema_version: Mapped[str] = mapped_column(String(10))
    session_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    camera_id: Mapped[str] = mapped_column(String(100))
    room_code: Mapped[str | None] = mapped_column(String(100))
    room_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('rooms.id', ondelete='RESTRICT'))
    source_type: Mapped[str] = mapped_column(String(10))
    frame_index: Mapped[int] = mapped_column(BigInteger)
    timestamp_ms: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
    people_count: Mapped[int] = mapped_column(Integer)
    tracked_count: Mapped[int] = mapped_column(Integer)
    line_enabled: Mapped[bool] = mapped_column(Boolean)
    in_count: Mapped[int | None] = mapped_column(BigInteger)
    out_count: Mapped[int | None] = mapped_column(BigInteger)
    initial_occupancy: Mapped[int | None] = mapped_column(BigInteger)
    estimated_occupancy: Mapped[int | None] = mapped_column(BigInteger)
    occupancy_underflow: Mapped[bool] = mapped_column(Boolean)
