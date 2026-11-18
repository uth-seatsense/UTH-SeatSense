from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class CountEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    session_id: UUID
    room_id: int = Field(gt=0)
    device_id: str = Field(min_length=1, max_length=100)
    direction: Literal["in", "out"]
    event_time: AwareDatetime
    device_status: Literal["online", "offline", "error"]

    @field_validator("event_time")
    @classmethod
    def normalize_utc(cls, value: datetime) -> datetime:
        return value.astimezone(timezone.utc)

    @field_validator("device_id")
    @classmethod
    def nonblank_device(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("device_id must not be blank")
        return value


class CountEventReceipt(BaseModel):
    event_id: UUID
    room_id: int
    received_at: datetime
    duplicate: bool = False
