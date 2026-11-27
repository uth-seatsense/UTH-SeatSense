import json
from datetime import datetime, timezone

import httpx
import pytest

from app.event_client import EventClient
from app.event_queue import EventQueue


def client(tmp_path, **kwargs):
    return EventClient(
        backend_url="http://backend", api_key="local-test-key", room_id=14,
        queue_path=tmp_path / "queue.json", **kwargs,
    )


def test_event_payload_matches_contract_and_hides_track_id(tmp_path):
    sender = client(tmp_path)
    sender.enqueue_crossing("IN", datetime(2026, 11, 22, tzinfo=timezone.utc))
    payload = sender.queue.first()
    assert set(payload) == {"event_id", "session_id", "room_id", "device_id", "direction", "event_time", "device_status"}
    assert payload["direction"] == "in"
    assert payload["event_time"].endswith("+00:00")
    assert "track_id" not in payload
    json.loads(json.dumps(payload))


def test_event_queue_persists_fifo_and_rejects_overflow(tmp_path):
    path = tmp_path / "queue.json"
    queue = EventQueue(path, max_events=2)
    queue.enqueue({"event_id": "one"})
    queue.enqueue({"event_id": "two"})
    assert EventQueue(path, max_events=2).first() == {"event_id": "one"}
    with pytest.raises(OverflowError):
        queue.enqueue({"event_id": "three"})
    queue.acknowledge("one")
    assert queue.first() == {"event_id": "two"}


def test_flush_retries_same_event_and_acknowledges(tmp_path):
    sender = client(tmp_path, retry_delays=(1, 2, 4))
    sender.enqueue_crossing("out")
    attempts = []

    def respond(request):
        attempts.append(json.loads(request.content))
        if len(attempts) == 1:
            raise httpx.ConnectError("offline", request=request)
        return httpx.Response(201, json={"duplicate": False})

    transport = httpx.MockTransport(respond)
    with httpx.Client(transport=transport) as http:
        assert sender.flush(http, sleep=lambda _: None) == 1
    assert attempts[0] == attempts[1]
    assert len(sender.queue) == 0


def test_flush_retains_event_after_retry_limit(tmp_path):
    sender = client(tmp_path, retry_delays=(1, 2, 4))
    sender.enqueue_crossing("in")
    transport = httpx.MockTransport(lambda request: (_ for _ in ()).throw(httpx.ConnectError("offline", request=request)))
    with httpx.Client(transport=transport) as http:
        assert sender.flush(http, sleep=lambda _: None) == 0
    assert len(sender.queue) == 1


def test_status_heartbeat_uses_dedicated_endpoint(tmp_path):
    sender = client(tmp_path)
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"device_status": "offline"})

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        assert sender.send_status_heartbeat("offline", client=http)
    request = requests[0]
    assert request.method == "PUT"
    assert request.url.path == "/api/v1/cv/devices/camera-01/status"
    assert json.loads(request.content)["device_status"] == "offline"


def test_duplicate_receipt_and_invalid_receipt_are_handled(tmp_path):
    sender = client(tmp_path)
    sender.enqueue_crossing("in")

    def duplicate(request):
        payload = json.loads(request.content)
        return httpx.Response(201, json={"event_id": payload["event_id"], "duplicate": True})

    with httpx.Client(transport=httpx.MockTransport(duplicate)) as http:
        assert sender.flush(http, sleep=lambda _: None) == 1
    assert len(sender.queue) == 0

    sender.enqueue_crossing("out")

    def wrong_receipt(request):
        return httpx.Response(201, json={"event_id": "00000000-0000-0000-0000-000000000000"})

    with httpx.Client(transport=httpx.MockTransport(wrong_receipt)) as http:
        with pytest.raises(RuntimeError, match="did not match"):
            sender.flush(http, sleep=lambda _: None)
    assert len(sender.queue) == 1


def test_invalid_payload_and_room_are_rejected(tmp_path):
    with pytest.raises(ValueError):
        client(tmp_path, room_id=0).enqueue_crossing("in")
    with pytest.raises(ValueError):
        client(tmp_path).enqueue_crossing("left")
