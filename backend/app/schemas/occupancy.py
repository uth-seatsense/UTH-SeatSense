from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_serializer, field_validator

MAX_ROOM_ID = 2**63 - 1
MAX_OCCUPIED_COUNT = 2**31 - 1


def _require_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("observed_at must include a timezone")
    return value.astimezone(timezone.utc)


class OccupancyObservationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: UUID
    room_id: StrictInt = Field(gt=0, le=MAX_ROOM_ID)
    occupied_count: StrictInt = Field(ge=0, le=MAX_OCCUPIED_COUNT)
    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def normalize_observed_at(cls, value: datetime) -> datetime:
        return _require_aware_utc(value)


class OccupancyObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_id: UUID
    room_id: int
    occupied_count: int
    observed_at: datetime
    source: Literal["cv"]

    @field_validator("observed_at", mode="before")
    @classmethod
    def normalize_database_timestamp(cls, value: datetime) -> datetime:
        # SQLite drops timezone metadata; persisted values are normalized to UTC
        # on ingestion, so a naive timestamp read back in tests represents UTC.
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_serializer("observed_at")
    def serialize_observed_at(self, value: datetime) -> str:
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

class CurrentOccupancyResponse(BaseModel):
    current_count: int | None
    updated_at: datetime | None
    location: str

    model_config = ConfigDict(from_attributes=True)
