from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.campus import Campus
from app.models.count_event import CountEvent
from app.models.counting_session import CountingSession
from app.models.cv_count_record import CVCountRecord
from app.models.room import Room
from app.models.user import User
from main import app


OCCUPANCY = "/api/v1/occupancy"
STAFF = {"Authorization": "Bearer staff-token"}
STUDENT = {"Authorization": "Bearer student-token"}
CV = {"X-API-Key": "test-cv-key"}


@pytest.fixture
def api(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models = (AuthSession, Campus, CountEvent, CountingSession, CVCountRecord, Room, User)
    Base.metadata.create_all(engine, tables=[model.__table__ for model in models])
    factory = sessionmaker(engine, expire_on_commit=False)
    now = datetime.now(timezone.utc)
    with factory.begin() as db:
        db.execute(text(
            "ALTER TABLE rooms ADD COLUMN capacity_confirmed BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        db.add_all([
            Campus(campus_id=1, code="CS1", name="Co so 1"),
            Campus(campus_id=3, code="CS3", name="Co so 3"),
            Room(id=14, code="A101", name="A101", capacity=40, campus_id=1),
            Room(id=15, code="B201", name="B201", capacity=20, campus_id=3),
            User(user_id=1, display_name="Staff", email="staff@example.test", role="librarian"),
            User(user_id=2, display_name="Student", email="student@example.test", role="student"),
        ])
        db.flush()
        db.execute(text("UPDATE rooms SET capacity_confirmed = TRUE WHERE id = 14"))
        for user_id, token in [(1, "staff-token"), (2, "student-token")]:
            db.add(AuthSession(
                user_id=user_id, token_hash=sha256(token.encode()).hexdigest(),
                created_at=now, expires_at=now + timedelta(hours=1),
            ))

    def test_db():
        with factory() as db:
            yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, test_db)
    monkeypatch.setattr(settings, "cv_ingest_api_key", SecretStr(CV["X-API-Key"]))
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        engine.dispose()


def start_session(client, initial_count, room_id=14):
    response = client.post(
        f"{OCCUPANCY}/rooms/{room_id}/counting-sessions",
        json={"initial_count": initial_count},
        headers=STAFF,
    )
    assert response.status_code == 201, response.text
    return response.json()


def latest(client, room_id=14):
    response = client.get(f"{OCCUPANCY}/rooms/{room_id}/latest")
    assert response.status_code == 200, response.text
    return response.json()


def crossing(direction="in", **overrides):
    return {
        "event_id": str(uuid4()),
        "session_id": str(uuid4()),
        "room_id": 14,
        "device_id": "cam-01",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "device_status": "online",
        "direction": direction,
        **overrides,
    }


def send_event(client, event):
    response = client.post("/api/v1/cv/events", json=event, headers=CV)
    assert response.status_code == 201, response.text
    return response.json()


def test_initial_count_and_unique_crossings_reach_all_read_endpoints(api):
    client, factory = api
    with factory.begin() as db:
        db.add(CVCountRecord(
            schema_version="1.0", session_id=uuid4(), camera_id="cam-01",
            room_id=14, room_code="A101", source_type="webcam", frame_index=1,
            timestamp_ms=0, recorded_at=datetime.now(timezone.utc),
            people_count=8, tracked_count=8, line_enabled=False,
            occupancy_underflow=False,
        ))
    missing = latest(client)
    assert missing["occupancy_status"] == "insufficient"
    assert missing["estimated_occupancy"] is None
    assert missing["available_seats"] is None

    session = start_session(client, 10)
    assert session["started_by"] == 1
    assert latest(client)["estimated_occupancy"] == 10
    for _ in range(3):
        event = crossing()
        assert send_event(client, event)["duplicate"] is False
    assert send_event(client, event)["duplicate"] is True

    state = latest(client)
    assert state["estimated_occupancy"] == 13
    assert state["available_seats"] == 27
    assert state["occupancy_status"] == "fresh"

    status = client.get(f"{OCCUPANCY}/rooms/status").json()
    assert [room["current_count"] for room in status["rooms"]] == [13, None]
    assert status["total_people_in_rooms"] is None
    assert client.get(f"{OCCUPANCY}/current?campus=CS1").json()["current_count"] == 13
    overall = client.get(f"{OCCUPANCY}/current").json()
    assert overall["current_count"] is None
    assert overall["data_status"] == "insufficient"


def test_new_session_ignores_old_and_offline_crossings(api):
    client, factory = api
    old = start_session(client, 10)
    send_event(client, crossing())
    new = start_session(client, 4)
    send_event(client, crossing(event_time=old["started_at"]))
    send_event(client, crossing(device_status="offline"))
    send_event(client, crossing("out"))

    assert latest(client)["estimated_occupancy"] == 3
    with factory() as db:
        sessions = db.scalars(select(CountingSession).order_by(CountingSession.id)).all()
        assert [session.id for session in sessions] == [old["id"], new["id"]]
        assert sessions[0].ended_at == sessions[1].started_at
        assert sessions[1].ended_at is None


def test_unconfirmed_capacity_is_insufficient_after_start(api):
    client, _ = api
    start_session(client, 10, room_id=15)
    send_event(client, crossing(room_id=15))

    state = latest(client, room_id=15)
    assert state["occupancy_status"] == "insufficient"
    assert state["estimated_occupancy"] is None
    assert state["available_seats"] is None


def test_floor_applies_to_net_total_and_seats(api):
    client, _ = api
    start_session(client, 0)
    send_event(client, crossing("out"))
    assert latest(client)["estimated_occupancy"] == 0
    send_event(client, crossing())
    assert latest(client)["estimated_occupancy"] == 0

    start_session(client, 41)
    state = latest(client)
    assert state["estimated_occupancy"] == 41
    assert state["available_seats"] == 0
    assert state["over_capacity"] is True


def test_start_requires_authorized_operator_and_initial_headcount(api):
    client, _ = api
    url = f"{OCCUPANCY}/rooms/14/counting-sessions"
    assert client.post(url, json={"initial_count": 10}).status_code == 401
    assert client.post(url, json={"initial_count": 10}, headers=STUDENT).status_code == 403
    for payload in ({}, {"initial_count": -1}, {"initial_count": "10"}):
        assert client.post(url, json=payload, headers=STAFF).status_code == 422
    response = client.post(
        f"{OCCUPANCY}/rooms/999/counting-sessions",
        json={"initial_count": 0},
        headers=STAFF,
    )
    assert response.status_code == 404
