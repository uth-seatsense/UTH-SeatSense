from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.models.cv_count_record import CVCountRecord
from app.models.room import Room
from main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Room.__table__.create(engine)
    CVCountRecord.__table__.create(engine)
    session_factory = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as db:
            yield db

    with session_factory() as db:
        db.add_all(
            [
                Room(
                    id=14,
                    code="A101",
                    name="Room A101",
                    capacity=40,
                    created_at=datetime.now(timezone.utc),
                ),
                Room(
                    id=15,
                    code="B201",
                    name="Room B201",
                    capacity=60,
                    created_at=datetime.now(timezone.utc),
                ),
            ]
        )
        db.commit()

    app.dependency_overrides[get_db] = override_get_db
    app.state.cv_test_session_factory = session_factory
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        del app.state.cv_test_session_factory
        engine.dispose()


def cv_record(**changes: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "1.0",
        "session_id": str(uuid4()),
        "camera_id": "cam-01",
        "room_id": "A101",
        "source_type": "webcam",
        "frame_index": 100,
        "timestamp_ms": 10000.0,
        "recorded_at": "2026-10-30T00:00:00Z",
        "people_count": 3,
        "tracked_count": 2,
        "line_enabled": True,
        "in_count": 4,
        "out_count": 1,
        "initial_occupancy": 0,
        "estimated_occupancy": 3,
        "occupancy_underflow": False,
    }
    record.update(changes)
    return record


def test_cv_batch_receipt_and_idempotent_retry(client: TestClient) -> None:
    request = {"records": [cv_record(), cv_record(frame_index=101)]}

    first = client.post("/api/v1/cv/count-records", json=request)
    assert first.status_code == 200
    assert first.json()["created_count"] == 2
    assert first.json()["duplicate_count"] == 0
    assert first.json()["records"][0] == {
        "record_id": 1,
        "session_id": request["records"][0]["session_id"],
        "frame_index": 100,
        "room_code": "A101",
        "room_id": 14,
        "received_at": first.json()["records"][0]["received_at"],
        "duplicate": False,
    }
    assert first.json()["records"][0]["received_at"].endswith("Z")

    retry = client.post("/api/v1/cv/count-records", json=request)
    assert retry.status_code == 200
    assert retry.json()["created_count"] == 0
    assert retry.json()["duplicate_count"] == 2
    assert all(item["duplicate"] for item in retry.json()["records"])


def test_conflicting_record_rolls_back_the_entire_batch(client: TestClient) -> None:
    original = cv_record()
    response = client.post(
        "/api/v1/cv/count-records",
        json={"records": [original, cv_record(**{**original, "people_count": 4})]},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "cv_record_conflict"
    with app.state.cv_test_session_factory() as db:
        count = db.scalar(select(func.count()).select_from(CVCountRecord))
    assert count == 0


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"people_count": -1}, "people_count"),
        ({"tracked_count": 4}, "tracked_count"),
        ({"frame_index": "100"}, "frame_index"),
        ({"recorded_at": "2026-10-30T00:00:00"}, "recorded_at"),
        ({"estimated_occupancy": 9}, "estimated_occupancy"),
        ({"unknown": True}, "unknown"),
    ],
)
def test_invalid_cv_record_returns_contract_validation_error(
    client: TestClient, changes: dict[str, object], field: str
) -> None:
    response = client.post(
        "/api/v1/cv/count-records",
        json={"records": [cv_record(**changes)]},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert any(field in item["field"] for item in response.json()["error"]["details"])


def test_empty_batch_and_malformed_json_are_rejected(client: TestClient) -> None:
    empty = client.post("/api/v1/cv/count-records", json={"records": []})
    malformed = client.post(
        "/api/v1/cv/count-records",
        content="{not-json",
        headers={"Content-Type": "application/json"},
    )

    assert empty.status_code == 422
    assert empty.json()["error"]["code"] == "validation_error"
    assert malformed.status_code == 400
    assert malformed.json()["error"]["code"] == "malformed_json"


def test_latest_live_occupancy_filters_webcam_and_preserves_zero(
    client: TestClient,
) -> None:
    video = cv_record(source_type="video", frame_index=100)
    live_zero = cv_record(
        source_type="webcam",
        frame_index=101,
        people_count=0,
        tracked_count=0,
        in_count=0,
        out_count=0,
        estimated_occupancy=0,
    )
    response = client.post(
        "/api/v1/cv/count-records", json={"records": [video, live_zero]}
    )
    assert response.status_code == 200

    latest = client.get("/api/v1/occupancy/rooms/14/latest")
    assert latest.status_code == 200
    assert latest.json()["estimated_occupancy"] == 0
    assert latest.json()["source_type"] == "webcam"
    assert latest.json()["room_code"] == "A101"
    assert latest.json()["is_stale"] is False

    with app.state.cv_test_session_factory() as db:
        record = db.scalar(
            select(CVCountRecord).where(CVCountRecord.frame_index == 101)
        )
        assert record is not None
        record.received_at = datetime.now(timezone.utc) - timedelta(seconds=31)
        db.commit()

    stale = client.get("/api/v1/occupancy/rooms/14/latest")
    assert stale.status_code == 200
    assert stale.json()["is_stale"] is True


def test_latest_distinguishes_missing_data_and_unknown_room(
    client: TestClient,
) -> None:
    no_data = client.get("/api/v1/occupancy/rooms/15/latest")
    unknown_room = client.get("/api/v1/occupancy/rooms/999/latest")

    assert no_data.status_code == 404
    assert no_data.json()["error"]["code"] == "occupancy_not_found"
    assert unknown_room.status_code == 404
    assert unknown_room.json()["error"]["code"] == "room_not_found"


def test_database_failure_uses_service_unavailable_envelope(
    client: TestClient,
) -> None:
    def unavailable_database():
        raise OperationalError("SELECT 1", {}, RuntimeError("database offline"))

    app.dependency_overrides[get_db] = unavailable_database
    try:
        response = client.get("/api/v1/occupancy/rooms/14/latest")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"
