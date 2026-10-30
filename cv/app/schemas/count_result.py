"""Versioned transport-neutral CV output."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class CountResult(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    session_id: str = Field(min_length=1)
    camera_id: str = Field(min_length=1, max_length=100)
    room_id: str | None = Field(default=None, min_length=1, max_length=100)
    source_type: Literal["video"] = "video"
    frame_index: int = Field(ge=0)
    timestamp_ms: float = Field(ge=0)
    recorded_at: AwareDatetime
    people_count: int = Field(ge=0)
    tracked_count: int = Field(ge=0)
    line_enabled: bool
    in_count: int | None = Field(default=None, ge=0)
    out_count: int | None = Field(default=None, ge=0)
    initial_occupancy: int | None = Field(default=None, ge=0)
    estimated_occupancy: int | None = Field(default=None, ge=0)
    occupancy_underflow: bool = False

    @model_validator(mode="after")
    def consistency(self):
        if self.tracked_count > self.people_count:
            raise ValueError("tracked_count exceeds people_count")
        if self.line_enabled and (self.in_count is None or self.out_count is None):
            raise ValueError("Enabled line requires both counters")
        if not self.line_enabled and any(v is not None for v in (self.in_count, self.out_count, self.initial_occupancy)):
            raise ValueError("Disabled line cannot have counters or initial occupancy")
        raw = None if self.initial_occupancy is None else self.initial_occupancy + self.in_count - self.out_count
        if self.estimated_occupancy != (None if raw is None else max(0, raw)) or self.occupancy_underflow != (raw is not None and raw < 0):
            raise ValueError("Inconsistent occupancy estimate")
        return self


class CrossingEvent(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    event_id: str
    session_id: str
    camera_id: str
    room_id: str | None = None
    frame_index: int = Field(ge=0)
    timestamp_ms: float = Field(ge=0)
    recorded_at: AwareDatetime
    track_id: int = Field(ge=1)
    direction: Literal["IN", "OUT"]
    confidence: float = Field(ge=0, le=1)
