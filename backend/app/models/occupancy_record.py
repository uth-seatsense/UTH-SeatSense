from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OccupancyRecord(Base):
    __tablename__ = "occupancy_records"
    __table_args__ = (
        Index(
            "idx_occupancy_room_observed",
            "room_id",
            "observed_at",
            "id",
        ),
        Index(
            "uq_occupancy_records_observation_id",
            "observation_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    observation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    room_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("rooms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    occupied_count: Mapped[int] = mapped_column(Integer, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    source: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'cv'")
    )
