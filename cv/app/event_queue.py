"""Persistent FIFO queue for CV events, stored atomically as local JSON."""
import json
import os
import tempfile
from pathlib import Path


class EventQueue:
    def __init__(self, path, max_events=10000):
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self.path = Path(path)
        self.max_events = max_events
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self):
        try:
            events = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Cannot read event queue {self.path}") from exc
        if not isinstance(events, list) or not all(isinstance(item, dict) for item in events):
            raise RuntimeError("Event queue has an invalid format")
        if len(events) > self.max_events:
            raise RuntimeError("Stored queue exceeds configured max_events")
        return events

    def _save(self, events):
        fd, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=f".{self.path.name}.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(events, output, separators=(",", ":"))
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def __len__(self):
        return len(self._load())

    def enqueue(self, event):
        events = self._load()
        if len(events) >= self.max_events:
            raise OverflowError("CV event queue is full; no event was discarded")
        events.append(dict(event))
        self._save(events)

    def first(self):
        events = self._load()
        return events[0] if events else None

    def acknowledge(self, event_id):
        events = self._load()
        if not events or events[0].get("event_id") != event_id:
            raise ValueError("Only the first queued event can be acknowledged")
        self._save(events[1:])
