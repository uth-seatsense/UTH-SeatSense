from collections.abc import Generator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.db.session import get_db
from app.core.config import settings
from app.models.count_event import CountEvent
from app.models.occupancy_record import OccupancyRecord
from app.models.room import Room
from main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Room.__table__.create(engine)
    CountEvent.__table__.create(engine)
    OccupancyRecord.__table__.create(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    def override_db():
        with factory() as db:
            yield db
    with factory() as db:
        db.add(Room(id=14, code="A101", name="Room A101", capacity=40, created_at=datetime.now(timezone.utc)))
        db.commit()
    app.dependency_overrides[get_db] = override_db
    previous_api_key = settings.cv_ingest_api_key
    settings.cv_ingest_api_key = SecretStr("test-cv-key")
    app.state.count_event_test_factory = factory
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)
        settings.cv_ingest_api_key = previous_api_key
        engine.dispose()


def payload(**updates):
    value = {"event_id": str(uuid4()), "session_id": str(uuid4()), "room_id": 14,
             "device_id": "cam-01", "direction": "in", "event_time": "2026-11-18T01:00:00Z",
             "device_status": "online"}
    value.update(updates)
    return value


def cv_headers(api_key: str = "test-cv-key") -> dict[str, str]:
    return {"X-API-Key": api_key}


def test_event_created_and_same_event_is_idempotent(client):
    body = payload()
    created = client.post("/api/v1/cv/events", json=body, headers=cv_headers())
    duplicate = client.post("/api/v1/cv/events", json=body, headers=cv_headers())
    assert created.status_code == 201 and created.json()["duplicate"] is False
    assert duplicate.status_code == 201 and duplicate.json()["duplicate"] is True
    with app.state.count_event_test_factory() as db:
        assert db.scalar(select(func.count()).select_from(CountEvent)) == 1


def test_event_updates_occupancy_once_and_retry_does_not_double_apply(client):
    body = payload(direction="in")
    created = client.post("/api/v1/cv/events", json=body, headers=cv_headers())
    duplicate = client.post("/api/v1/cv/events", json=body, headers=cv_headers())

    assert created.status_code == 201
    assert duplicate.status_code == 201
    assert duplicate.json()["duplicate"] is True
    with app.state.count_event_test_factory() as db:
        record = db.scalar(
            select(OccupancyRecord).order_by(OccupancyRecord.id.desc()).limit(1)
        )
        assert record is not None
        assert record.current_count == 1


def test_different_payload_with_existing_event_id_conflicts(client):
    body = payload()
    assert client.post("/api/v1/cv/events", json=body, headers=cv_headers()).status_code == 201
    conflict = client.post("/api/v1/cv/events", json={**body, "direction": "out"}, headers=cv_headers())
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "event_id_conflict"


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "wrong-key"}])
def test_api_key_required(client, headers):
    response = client.post("/api/v1/cv/events", json=payload(), headers=headers)
    assert response.status_code == 401


def test_invalid_direction_returns_422(client):
    response = client.post("/api/v1/cv/events", json=payload(direction="left"), headers=cv_headers())
    assert response.status_code == 422


def test_unknown_room_returns_404(client):
    response = client.post(
        "/api/v1/cv/events",
        json=payload(room_id=9999),
        headers=cv_headers(),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "room_not_found"


def test_malformed_json_returns_400(client):
    response = client.post(
        "/api/v1/cv/events",
        content=b"{",
        headers={**cv_headers(), "Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "malformed_json"


def test_extra_field_returns_422(client):
    response = client.post(
        "/api/v1/cv/events",
        json=payload(track_id="must-not-be-persisted"),
        headers=cv_headers(),
    )
    assert response.status_code == 422
