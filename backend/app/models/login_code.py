from datetime import datetime

from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, synonym

from app.db.base import Base


class LoginCode(Base):
    __tablename__ = "email_otp_challenges"

    challenge_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    otp_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Logical ERD names map to the existing physical columns.
    code_id = synonym("challenge_id")
    code_hash = synonym("otp_hash")
    used_at = synonym("consumed_at")
