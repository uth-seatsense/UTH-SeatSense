from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Boolean, DateTime, Identity, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    building: Mapped[str | None] = mapped_column(String(150))
    capacity: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
