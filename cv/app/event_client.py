"""Authenticated CV event sender with stable IDs and bounded retries."""
import argparse
import os
import logging
import math
import time
from datetime import datetime, timezone
from uuid import UUID, uuid4

import httpx

from app.event_queue import EventQueue

logger = logging.getLogger(__name__)


class EventClient:
    def __init__(self, backend_url=None, api_key=None, queue_path=None,
                 room_id=None, device_id=None, max_events=10000,
                 retry_delays=(1, 2, 4), timeout=3, total_timeout=10):
        self.backend_url = (backend_url if backend_url is not None else os.getenv("BACKEND_URL", "")).rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("CV_API_KEY", "")
        self.room_id = room_id if room_id is not None else os.getenv("CV_ROOM_ID", "")
        self.device_id = device_id if device_id is not None else os.getenv("CV_DEVICE_ID", os.getenv("CV_CAMERA_ID", "camera-01"))
        self.session_id = str(uuid4())
        self._device_status = "online"
        self.queue = EventQueue(queue_path or os.getenv("CV_EVENT_QUEUE_PATH", "outputs/event-queue.json"), max_events)
        self.retry_delays = tuple(retry_delays)
        if any(not isinstance(delay, (int, float)) or not math.isfinite(delay) or delay < 0 for delay in self.retry_delays):
            raise ValueError("Retry delays must be finite and nonnegative")
        if not math.isfinite(timeout) or not math.isfinite(total_timeout) or timeout <= 0 or total_timeout <= 0:
            raise ValueError("Request timeouts must be positive")
        self.timeout = timeout
        self.total_timeout = total_timeout

    @property
    def enabled(self):
        return bool(self.backend_url and self.api_key and self.room_id)

    def make_event(self, direction, device_status=None, event_time=None):
        if not self.room_id:
            raise ValueError("CV_ROOM_ID must identify a configured backend room")
        device_status = device_status or self._device_status
        if direction not in {"in", "out"} or device_status not in {"online", "offline", "error"}:
            raise ValueError("Invalid count event direction or device status")
        if not 1 <= int(self.room_id) or not self.device_id.strip() or len(self.device_id) > 100:
            raise ValueError("A valid room ID and device ID are required")
        payload = {
            "event_id": str(uuid4()), "session_id": self.session_id,
            "room_id": int(self.room_id), "device_id": self.device_id,
            "direction": direction,
            "event_time": (event_time or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(),
            "device_status": device_status,
        }
        self._validate_payload(payload)
        return payload

    @staticmethod
    def _validate_payload(payload):
        required = {"event_id", "session_id", "room_id", "device_id", "direction", "event_time", "device_status"}
        if set(payload) != required:
            raise ValueError("CountEvent fields do not match the Backend schema")
        UUID(payload["event_id"])
        UUID(payload["session_id"])
        if not isinstance(payload["room_id"], int) or payload["room_id"] < 1:
            raise ValueError("room_id must be a positive integer")
        if not 1 <= len(payload["device_id"].strip()) <= 100:
            raise ValueError("device_id must contain 1 to 100 nonblank characters")
        if payload["direction"] not in {"in", "out"}:
            raise ValueError("direction must be 'in' or 'out'")
        if payload["device_status"] not in {"online", "offline", "error"}:
            raise ValueError("Unsupported device status")
        event_time = datetime.fromisoformat(payload["event_time"].replace("Z", "+00:00"))
        if event_time.tzinfo is None or event_time.utcoffset() != timezone.utc.utcoffset(event_time):
            raise ValueError("event_time must be ISO 8601 UTC")
        return payload

    def enqueue_crossing(self, direction, event_time=None):
        event = self.make_event(direction.lower(), event_time=event_time)
        self.queue.enqueue(event)
        return event["event_id"]

    def enqueue_status(self, status):
        if status not in {"online", "offline", "error"}:
            raise ValueError("Unsupported device status")
        return self.send_status_heartbeat(status)

    def flush(self, client=None, sleep=time.sleep):
        if not self.enabled:
            return 0
        sent = 0
        owned = client is None
        client = client or httpx.Client(timeout=httpx.Timeout(self.timeout, read=self.total_timeout))
        try:
            while event := self.queue.first():
                acknowledged = False
                for attempt in range(len(self.retry_delays) + 1):
                    try:
                        response = client.post(
                            f"{self.backend_url}/api/v1/cv/events", json=event,
                            headers={"X-API-Key": self.api_key},
                        )
                        if response.status_code in {200, 201}:
                            receipt = response.json()
                            if receipt.get("event_id") != event["event_id"]:
                                raise RuntimeError("CV event receipt event_id did not match request")
                            acknowledged = True
                            break
                        if response.status_code < 500:
                            if response.status_code == 409 and response.json().get("error", {}).get("code") == "event_id_conflict":
                                logger.error("CV event %s has an idempotency conflict and remains at queue head", event["event_id"])
                                return sent
                            raise RuntimeError(f"CV event rejected ({response.status_code}): {response.text}")
                    except httpx.HTTPError:
                        pass
                    if attempt < len(self.retry_delays):
                        sleep(self.retry_delays[attempt])
                if not acknowledged:
                    break
                self.queue.acknowledge(event["event_id"])
                self._device_status = event["device_status"]
                sent += 1
            return sent
        finally:
            if owned:
                client.close()

    def send_status_heartbeat(self, status, reported_at=None, client=None):
        if status not in {"online", "offline", "error"}:
            raise ValueError("Unsupported device status")
        if not self.enabled:
            return False
        owned = client is None
        client = client or httpx.Client(timeout=httpx.Timeout(self.timeout, read=self.total_timeout))
        try:
            quoted_device_id = httpx.URL("http://local").copy_with(path="/" + self.device_id).path.lstrip("/")
            response = client.put(
                f"{self.backend_url}/api/v1/cv/devices/{quoted_device_id}/status",
                json={"room_id": int(self.room_id), "device_status": status,
                      "reported_at": (reported_at or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()},
                headers={"X-API-Key": self.api_key},
            )
            response.raise_for_status()
            try:
                response.json()
            except ValueError:
                pass
            self._device_status = status
            return True
        finally:
            if owned:
                client.close()


def main():
    parser = argparse.ArgumentParser(description="Flush the durable CV event queue to Backend")
    parser.add_argument("--queue", default=os.getenv("CV_EVENT_QUEUE_PATH", "outputs/event-queue.json"))
    parser.add_argument("--room-id", type=int, default=None)
    parser.add_argument("--device-id", default=None)
    args = parser.parse_args()
    sender = EventClient(queue_path=args.queue, room_id=args.room_id, device_id=args.device_id)
    if not sender.enabled:
        parser.error("Set BACKEND_URL, CV_API_KEY and CV_ROOM_ID before flushing events")
    print(f"Acknowledged {sender.flush()} queued event(s)")


if __name__ == "__main__":
    main()
