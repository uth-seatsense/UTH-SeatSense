from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class CheckInTokenRead(BaseModel):
    booking_id: int
    qr_token: str
    valid_from: datetime
    expires_at: datetime

    @field_validator("valid_from", "expires_at", mode="before")
    @classmethod
    def normalize_times(cls, value: datetime) -> datetime:
        return _utc(value)


class CheckInCreate(BaseModel):
    booking_id: int = Field(gt=0)
    qr_token: str = Field(min_length=1, max_length=512)


class CheckInRead(BaseModel):
    booking_id: int
    status: Literal["checked_in"]
    checked_in_at: datetime

    @field_validator("checked_in_at", mode="before")
    @classmethod
    def normalize_time(cls, value: datetime) -> datetime:
        return _utc(value)
