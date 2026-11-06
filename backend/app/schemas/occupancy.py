from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_serializer, field_validator

MAX_ROOM_ID = 2**63 - 1
MAX_CURRENT_COUNT = 2**31 - 1


def _require_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("recorded_at must include a timezone")
    return value.astimezone(timezone.utc)


class OccupancyObservationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: UUID
    room_id: StrictInt = Field(gt=0, le=MAX_ROOM_ID)
    current_count: StrictInt = Field(ge=0, le=MAX_CURRENT_COUNT)
    recorded_at: datetime

    @field_validator("recorded_at")
    @classmethod
    def normalize_recorded_at(cls, value: datetime) -> datetime:
        return _require_aware_utc(value)


class OccupancyObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_id: UUID
    room_id: int
    current_count: int
    recorded_at: datetime
    source: Literal["cv"]

    @field_validator("recorded_at", mode="before")
    @classmethod
    def normalize_database_timestamp(cls, value: datetime) -> datetime:
        # SQLite drops timezone metadata; persisted values are normalized to UTC
        # on ingestion, so a naive timestamp read back in tests represents UTC.
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_serializer("recorded_at")
    def serialize_recorded_at(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
