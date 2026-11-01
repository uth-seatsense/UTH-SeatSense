from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_serializer,
    field_validator,
    model_validator,
)

MAX_BIGINT = 2**63 - 1
MAX_INT = 2**31 - 1


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        # SQLite drops timezone metadata when reading TIMESTAMPTZ test values.
        # Persisted timestamps are normalized to UTC before they are written.
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class CVCountInput(BaseModel):
    """One CV v1.0 frame aggregate as defined by the shared API contract."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    schema_version: Literal["1.0"] = "1.0"
    session_id: UUID
    camera_id: StrictStr = Field(min_length=1, max_length=100)
    room_id: StrictStr | None = Field(default=None, min_length=1, max_length=100)
    source_type: Literal["video", "webcam"] = "video"
    frame_index: StrictInt = Field(ge=0, le=MAX_BIGINT)
    timestamp_ms: StrictInt | StrictFloat = Field(ge=0)
    recorded_at: AwareDatetime
    people_count: StrictInt = Field(ge=0, le=MAX_INT)
    tracked_count: StrictInt = Field(ge=0, le=MAX_INT)
    line_enabled: StrictBool
    in_count: StrictInt | None = Field(default=None, ge=0, le=MAX_BIGINT)
    out_count: StrictInt | None = Field(default=None, ge=0, le=MAX_BIGINT)
    initial_occupancy: StrictInt | None = Field(default=None, ge=0, le=MAX_BIGINT)
    estimated_occupancy: StrictInt | None = Field(default=None, ge=0, le=MAX_BIGINT)
    occupancy_underflow: StrictBool = False

    @field_validator("camera_id", "room_id")
    @classmethod
    def identifiers_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("identifier must not be blank")
        return value

    @field_validator("recorded_at")
    @classmethod
    def normalize_recorded_at(cls, value: datetime) -> datetime:
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_counts(self) -> "CVCountInput":
        if self.tracked_count > self.people_count:
            raise ValueError("tracked_count must not exceed people_count")

        if self.line_enabled:
            if self.in_count is None or self.out_count is None:
                raise ValueError("line_enabled requires in_count and out_count")
        elif any(
            value is not None
            for value in (self.in_count, self.out_count, self.initial_occupancy)
        ):
            raise ValueError(
                "disabled line counting requires null counters and initial_occupancy"
            )

        if self.initial_occupancy is None:
            expected_occupancy = None
            expected_underflow = False
        else:
            # The line-enabled branch above guarantees both counters are present.
            raw_occupancy = self.initial_occupancy + self.in_count - self.out_count
            expected_occupancy = max(0, raw_occupancy)
            expected_underflow = raw_occupancy < 0

        if self.estimated_occupancy != expected_occupancy:
            raise ValueError("estimated_occupancy does not match the count formula")
        if self.occupancy_underflow != expected_underflow:
            raise ValueError("occupancy_underflow does not match the count formula")
        return self


class CVCountRead(BaseModel):
    """Persisted CV record, also used by the local persistence verification CLI."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    schema_version: str
    session_id: UUID
    camera_id: str
    room_code: str | None
    room_id: int | None
    source_type: str
    frame_index: int
    timestamp_ms: float
    recorded_at: datetime
    received_at: datetime
    people_count: int
    tracked_count: int
    line_enabled: bool
    in_count: int | None
    out_count: int | None
    initial_occupancy: int | None
    estimated_occupancy: int | None
    occupancy_underflow: bool

    @field_validator("recorded_at", "received_at", mode="before")
    @classmethod
    def normalize_timestamps(cls, value: datetime) -> datetime:
        return _utc(value)

    @field_serializer("recorded_at", "received_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return _utc(value).isoformat().replace("+00:00", "Z")


class CVCountBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[CVCountInput] = Field(min_length=1, max_length=1000)


class CVCountReceipt(BaseModel):
    record_id: int
    session_id: UUID
    frame_index: int
    room_code: str | None
    room_id: int | None
    received_at: datetime
    duplicate: bool

    @field_validator("received_at", mode="before")
    @classmethod
    def normalize_received_at(cls, value: datetime) -> datetime:
        return _utc(value)

    @field_serializer("received_at")
    def serialize_received_at(self, value: datetime) -> str:
        return _utc(value).isoformat().replace("+00:00", "Z")


class CVCountBatchResponse(BaseModel):
    status: Literal["accepted"] = "accepted"
    created_count: int
    duplicate_count: int
    records: list[CVCountReceipt]


class LatestRoomOccupancy(BaseModel):
    room_id: int
    room_code: str
    camera_id: str
    source_type: Literal["webcam"]
    people_count: int
    tracked_count: int
    estimated_occupancy: int | None
    occupancy_underflow: bool
    recorded_at: datetime
    received_at: datetime
    is_stale: bool

    @field_validator("recorded_at", "received_at", mode="before")
    @classmethod
    def normalize_timestamps(cls, value: datetime) -> datetime:
        return _utc(value)

    @field_serializer("recorded_at", "received_at")
    def serialize_timestamps(self, value: datetime) -> str:
        return _utc(value).isoformat().replace("+00:00", "Z")


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
