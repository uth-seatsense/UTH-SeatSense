"""Finite normalized line crossing using tracked bbox bottom centers."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class LineConfig:
    start: tuple[float, float]
    end: tuple[float, float]
    in_direction: str = "negative-to-positive"
    deadband: float = 0.01
    max_gap_ms: float = 1000
    cooldown_ms: float = 500

    def __post_init__(self):
        if len(self.start) != 2 or len(self.end) != 2 or not all(math.isfinite(v) and 0 <= v <= 1 for v in (*self.start, *self.end)):
            raise ValueError("Line endpoints must be normalized coordinates in [0,1]")
        if self.start == self.end:
            raise ValueError("Line endpoints must differ")
        if self.in_direction not in {"negative-to-positive", "positive-to-negative"}:
            raise ValueError("Invalid IN direction")
        if not all(math.isfinite(v) and v >= 0 for v in (self.deadband, self.max_gap_ms, self.cooldown_ms)) or self.max_gap_ms == 0:
            raise ValueError("Invalid line timing or deadband")


class LineCounter:
    def __init__(self, config):
        self.config = config
        self.states = {}
        self.in_count = 0
        self.out_count = 0

    def update(self, detections, width, height, timestamp_ms):
        cfg = self.config
        self.states = {key: value for key, value in self.states.items() if timestamp_ms - value[2] <= cfg.max_gap_ms}
        ax, ay = cfg.start
        dx, dy = cfg.end[0] - ax, cfg.end[1] - ay
        length = math.hypot(dx, dy)
        events = []
        for detection in detections:
            identity = detection["track_id"]
            if identity is None:
                continue
            x1, _, x2, y2 = detection["bbox_xyxy"]
            point = ((x1 + x2) / (2 * width), y2 / height)
            distance = (dx * (point[1] - ay) - dy * (point[0] - ax)) / length
            previous = self.states.get(identity)
            if abs(distance) <= cfg.deadband:
                if previous:
                    self.states[identity] = (previous[0], previous[1], timestamp_ms, previous[3])
                continue
            side = 1 if distance > 0 else -1
            last_event = previous[3] if previous else -math.inf
            if previous and previous[0] != side:
                old = previous[1]
                old_distance = dx * (old[1] - ay) - dy * (old[0] - ax)
                ratio = old_distance / (old_distance - distance * length)
                crossing = (old[0] + ratio * (point[0] - old[0]), old[1] + ratio * (point[1] - old[1]))
                projection = ((crossing[0] - ax) * dx + (crossing[1] - ay) * dy) / (length * length)
                if 0 <= projection <= 1 and timestamp_ms - last_event >= cfg.cooldown_ms:
                    is_in = (side == 1) == (cfg.in_direction == "negative-to-positive")
                    self.in_count += int(is_in)
                    self.out_count += int(not is_in)
                    events.append({"track_id": identity, "direction": "IN" if is_in else "OUT", "confidence": detection["confidence"]})
                    last_event = timestamp_ms
            self.states[identity] = (side, point, timestamp_ms, last_event)
        return events
