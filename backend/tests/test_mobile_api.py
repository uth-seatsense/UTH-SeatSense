from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import SecretStr

import app.models
from app.api.deps import get_db
from app.api.v1.endpoints import auth
from app.core.config import Settings
from app.db.base import Base
from app.models.campus import Campus
from app.models.email_otp_challenge import EmailOtpChallenge
from app.models.room import Room
from app.services.auth_service import _configuration_ready
from main import app


@pytest.fixture
def api(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[tuple[TestClient, list[tuple[str, str]]], None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as db:
            yield db

    settings = Settings(
        allowed_email_domains="uth.edu.vn",
        otp_hash_secret=SecretStr("test-only-secret-with-at-least-32-bytes"),
        smtp_host="smtp.test",
        smtp_from_email="noreply@uth.edu.vn",
    )
    sent_codes: list[tuple[str, str]] = []
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth.get_settings] = lambda: settings
    app.state.test_engine = engine
    monkeypatch.setattr(
        auth,
        "send_otp_email",
        lambda _settings, email, otp: sent_codes.append((email, otp)),
    )

    with session_factory() as db:
        campus = Campus(code="CS1", name="Cơ sở 1")
        db.add(campus)
        db.flush()
        db.add_all(
            [
                Room(
                    id=1,
                    code="F101",
                    name="Khu tự học",
                    room_type="reading_room",
                    capacity=40,
                    campus_id=campus.campus_id,
                ),
                Room(
                    id=2,
                    code="T201",
                    name="Phòng chuyên đề",
                    room_type="group_study_room",
                    capacity=6,
                    campus_id=campus.campus_id,
                ),
            ]
        )
        db.commit()

    try:
        with TestClient(app) as client:
            yield client, sent_codes
    finally:
        app.dependency_overrides.clear()
        del app.state.test_engine
        engine.dispose()


def _login(client: TestClient, sent_codes: list[tuple[str, str]], email: str) -> str:
    requested = client.post("/api/v1/auth/register", json={"email": email})
    assert requested.status_code == 202
    assert requested.json() == {"status": "otp_sent"}
    assert sent_codes[-1][0] == email
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": sent_codes[-1][1]},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def test_otp_auth_requires_long_secret_and_complete_smtp_credentials() -> None:
    settings = Settings(
        allowed_email_domains="uth.edu.vn",
        otp_hash_secret=SecretStr("short"),
        smtp_host="smtp.test",
        smtp_from_email="noreply@uth.edu.vn",
    )
    assert not _configuration_ready(settings)

    settings.otp_hash_secret = SecretStr("test-only-secret-with-at-least-32-bytes")
    settings.smtp_username = "smtp-user"
    assert not _configuration_ready(settings)

    settings.smtp_password = SecretStr("smtp-password")
    assert _configuration_ready(settings)


def test_email_otp_login_me_and_logout_revoke_session(
    api: tuple[TestClient, list[tuple[str, str]]],
) -> None:
    client, sent_codes = api
    token = _login(client, sent_codes, "student@uth.edu.vn")
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.get("/api/v1/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == "student@uth.edu.vn"
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_otp_domain_resend_and_attempt_limits(
    api: tuple[TestClient, list[tuple[str, str]]],
) -> None:
    client, sent_codes = api
    disallowed = client.post(
        "/api/v1/auth/register", json={"email": "student@example.com"}
    )
    assert disallowed.status_code == 422

    requested = client.post(
        "/api/v1/auth/register", json={"email": "student@uth.edu.vn"}
    )
    assert requested.status_code == 202
    assert sent_codes[-1][1] not in requested.text
    rate_limited = client.post(
        "/api/v1/auth/register", json={"email": "student@uth.edu.vn"}
    )
    assert rate_limited.status_code == 429

    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "student@uth.edu.vn", "otp": "000000"},
        )
        assert response.status_code == 401
    correct_after_lock = client.post(
        "/api/v1/auth/login",
        json={"email": "student@uth.edu.vn", "otp": sent_codes[-1][1]},
    )
    assert correct_after_lock.status_code == 401

    with Session(client.app.state.test_engine) as db:
        challenge = db.scalar(select(EmailOtpChallenge))
        assert challenge is not None
        assert challenge.attempts == 5
        assert challenge.consumed_at is not None


def test_room_booking_owner_limit_and_room_conflict(
    api: tuple[TestClient, list[tuple[str, str]]],
) -> None:
    client, sent_codes = api
    owner_token = _login(client, sent_codes, "owner@uth.edu.vn")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    rooms = client.get("/api/v1/rooms", headers=owner_headers)
    assert rooms.status_code == 200
    assert [item["room_type"] for item in rooms.json()["items"]] == [
        "free_area",
        "topic_room",
    ]
    assert rooms.json()["items"][0]["campus_code"] == "CS1"

    starts_at = datetime.now(timezone.utc) + timedelta(hours=2)
    ends_at = starts_at + timedelta(minutes=60)
    payload = {
        "room_id": 2,
        "starts_at": starts_at.isoformat(),
        "ends_at": ends_at.isoformat(),
        "participant_count": 4,
    }
    created = client.post("/api/v1/bookings", json=payload, headers=owner_headers)
    assert created.status_code == 201
    assert created.json()["status"] == "booked"
    assert created.json()["room"]["room_type"] == "topic_room"

    free_area = client.post(
        "/api/v1/bookings",
        json={**payload, "room_id": 1},
        headers=owner_headers,
    )
    assert free_area.status_code == 409
    assert free_area.json()["error"]["code"] == "room_not_bookable"

    daily_limit = client.post(
        "/api/v1/bookings",
        json={**payload, "room_id": 2, "starts_at": (starts_at + timedelta(hours=2)).isoformat(),
              "ends_at": (ends_at + timedelta(hours=2)).isoformat()},
        headers=owner_headers,
    )
    assert daily_limit.status_code == 409
    assert daily_limit.json()["error"]["code"] == "daily_limit_exceeded"

    other_token = _login(client, sent_codes, "other@uth.edu.vn")
    conflict = client.post(
        "/api/v1/bookings",
        json={**payload, "starts_at": (starts_at - timedelta(minutes=5)).isoformat(),
              "ends_at": (ends_at - timedelta(minutes=5)).isoformat()},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "booking_conflict"

    listed = client.get("/api/v1/bookings", headers=owner_headers)
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1


def test_qr_checkin_is_single_use(
    api: tuple[TestClient, list[tuple[str, str]]],
) -> None:
    import time

    client, sent_codes = api
    token = _login(client, sent_codes, "checkin@uth.edu.vn")
    headers = {"Authorization": f"Bearer {token}"}
    starts_at = datetime.now(timezone.utc) + timedelta(seconds=2)
    ends_at = starts_at + timedelta(minutes=60)
    created = client.post(
        "/api/v1/bookings",
        json={
            "room_id": 2,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
            "participant_count": 2,
        },
        headers=headers,
    )
    assert created.status_code == 201
    booking_id = created.json()["id"]

    qr = client.post(
        f"/api/v1/bookings/{booking_id}/check-in-token", headers=headers
    )
    assert qr.status_code == 201
    time.sleep(2.1)
    checked_in = client.post(
        "/api/v1/check-in",
        json={"booking_id": booking_id, "qr_token": qr.json()["qr_token"]},
        headers=headers,
    )
    assert checked_in.status_code == 200
    assert checked_in.json()["status"] == "checked_in"
    duplicate = client.post(
        "/api/v1/check-in",
        json={"booking_id": booking_id, "qr_token": qr.json()["qr_token"]},
        headers=headers,
    )
    assert duplicate.status_code == 409
