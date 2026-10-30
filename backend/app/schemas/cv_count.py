"""Backend validation of CV schema 1.0, independent of the CV runtime."""
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, field_validator, model_validator

MAX_BIGINT = 9223372036854775807
MAX_INT = 2147483647


class CVCountInput(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    schema_version: Literal['1.0'] = '1.0'
    session_id: UUID
    camera_id: str = Field(min_length=1, max_length=100)
    room_id: str | None = Field(default=None, min_length=1, max_length=100)
    source_type: Literal['video', 'webcam'] = 'video'
    frame_index: int = Field(ge=0, le=MAX_BIGINT)
    timestamp_ms: float = Field(ge=0)
    recorded_at: AwareDatetime
    people_count: int = Field(ge=0, le=MAX_INT)
    tracked_count: int = Field(ge=0, le=MAX_INT)
    line_enabled: bool
    in_count: int | None = Field(default=None, ge=0, le=MAX_BIGINT)
    out_count: int | None = Field(default=None, ge=0, le=MAX_BIGINT)
    initial_occupancy: int | None = Field(default=None, ge=0, le=MAX_BIGINT)
    estimated_occupancy: int | None = Field(default=None, ge=0, le=MAX_BIGINT)
    occupancy_underflow: bool = False

    @field_validator('camera_id', 'room_id')
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError('Identifier cannot be blank')
        return value

    @field_validator('recorded_at')
    @classmethod
    def utc(cls, value):
        return value.astimezone(timezone.utc)

    @model_validator(mode='after')
    def consistent(self):
        if self.tracked_count > self.people_count:
            raise ValueError('tracked_count exceeds people_count')
        if self.line_enabled and (self.in_count is None or self.out_count is None):
            raise ValueError('Line enabled requires both counters')
        if not self.line_enabled and any(v is not None for v in (self.in_count,self.out_count,self.initial_occupancy)):
            raise ValueError('Line disabled requires null counters and initial occupancy')
        raw = None if self.initial_occupancy is None else self.initial_occupancy + self.in_count - self.out_count
        if self.estimated_occupancy != (None if raw is None else max(0,raw)) or self.occupancy_underflow != (raw is not None and raw < 0):
            raise ValueError('Inconsistent occupancy estimate')
        return self


class CVCountRead(BaseModel):
    """room_id is the DB FK; room_code preserves CV's original room_id."""
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

    @field_validator('recorded_at', 'received_at')
    @classmethod
    def utc(cls, value):
        return value.astimezone(timezone.utc)
