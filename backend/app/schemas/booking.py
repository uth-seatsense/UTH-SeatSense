from datetime import datetime, timezone
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, field_validator

from app.schemas.room import RoomRead


class BookingCreate(BaseModel):
    room_id: int = Field(gt=0)
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    participant_count: int = Field(ge=2, le=6)

    @field_validator("starts_at", "ends_at")
    @classmethod
    def normalize_times(cls, value: datetime) -> datetime:
        return value.astimezone(timezone.utc)


class BookingRead(BaseModel):
    id: int
    room_id: int
    user_id: int
    participant_count: int
    status: Literal["booked", "checked_in", "completed", "cancelled", "no_show"]
    starts_at: datetime
    ends_at: datetime
    checkin_at: datetime | None
    no_show_at: datetime | None
    room: RoomRead

    @field_validator("starts_at", "ends_at", "checkin_at", "no_show_at", mode="before")
    @classmethod
    def normalize_response_times(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class BookingListResponse(BaseModel):
    items: list[BookingRead]
    limit: int
    offset: int
    total: int
