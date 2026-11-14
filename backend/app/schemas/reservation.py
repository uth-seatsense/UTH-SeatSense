"""Booking schemas prepared for the proposed bookings API."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    field_serializer,
    field_validator,
    model_validator,
)


class BookingCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: StrictInt = Field(gt=0)
    starts_at: datetime
    ends_at: datetime
    participant_count: StrictInt = Field(ge=2, le=6)

    @field_validator("starts_at", "ends_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_interval(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be later than starts_at")
        return self


class BookingRoomSummary(BaseModel):
    id: int
    code: str
    name: str
    capacity: int
    campus_id: int | None = None
    campus_code: str | None = None
    building: str | None = None


class BookingResponse(BaseModel):
    id: str
    room_id: int
    user_id: str
    participant_count: int | None
    status: Literal["booked", "checked_in", "completed", "cancelled", "no_show"]
    starts_at: datetime
    ends_at: datetime
    no_show_at: datetime | None = None
    room: BookingRoomSummary
    created_at: datetime

    @field_serializer("starts_at", "ends_at", "no_show_at", "created_at")
    def serialize_utc(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
