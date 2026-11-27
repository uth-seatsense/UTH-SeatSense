from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.api.deps import require_roles
from app.db.base import Base
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.booking import Booking
from app.models.counting_session import CountingSession
from app.models.room import Room
from app.models.user import User
from main import app


STAFF_PATH = "/api/v1/occupancy/rooms/1/counting-sessions"
BOOKING_BODY = {
    "room_id": 1,
    "starts_at": "2030-01-01T02:00:00Z",
    "ends_at": "2030-01-01T03:00:00Z",
    "participant_count": 2,
}
PROTECTED = [
    ("GET", "/api/v1/bookings", None),
    ("POST", "/api/v1/bookings", BOOKING_BODY),
    ("GET", "/api/v1/bookings/1", None),
    ("DELETE", "/api/v1/bookings/1", None),
    ("POST", "/api/v1/bookings/1/check-in-token", None),
    ("POST", "/api/v1/check-in", {"booking_id": 1, "qr_token": "test-token"}),
    ("POST", STAFF_PATH, {"initial_count": 3}),
]


@pytest.fixture
def api(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Import the session model explicitly so its table is available in isolation.
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    now = datetime.now(timezone.utc)
    with factory.begin() as db:
        db.execute(text(
            "ALTER TABLE rooms ADD COLUMN capacity_confirmed BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        db.add(Room(
            id=1, code="AUTHZ-1", name="Authz test room", capacity=6,
            room_type="group_study_room",
        ))
        for user_id, role in enumerate(
            ["student", "librarian", "admin", "student", "unknown"], start=1
        ):
            db.add(User(
                user_id=user_id, display_name=f"User {user_id}",
                email=f"user{user_id}@example.test", role=role,
                is_active=user_id != 4,
            ))
        db.flush()
        for token, user_id, expired, revoked in [
            ("student", 1, False, False),
            ("librarian", 2, False, False),
            ("admin", 3, False, False),
            ("inactive", 4, False, False),
            ("unknown-role", 5, False, False),
            ("expired", 1, True, False),
            ("revoked", 1, False, True),
        ]:
            db.add(AuthSession(
                user_id=user_id,
                token_hash=sha256(token.encode()).hexdigest(),
                created_at=now - timedelta(hours=2),
                expires_at=now + timedelta(hours=-1 if expired else 1),
                revoked_at=now if revoked else None,
            ))
        db.add(Booking(
            booking_id=1, user_id=2, room_id=1, participant_count=2,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2), status="booked",
        ))

    def test_db():
        with factory() as db:
            yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, test_db)
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        engine.dispose()


def headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("method,path,body", PROTECTED)
@pytest.mark.parametrize(
    "authorization",
    [None, "Bearer invalid", "Bearer expired", "Bearer revoked", "Basic abc", "Bearer"],
)
def test_protected_endpoints_reject_invalid_auth(api, method, path, body, authorization):
    client, factory = api
    response = client.request(
        method, path, json=body,
        headers={} if authorization is None else {"Authorization": authorization},
    )
    assert response.status_code == 401, response.text
    assert response.json()["error"]["code"] == "unauthorized"
    with factory() as db:
        assert db.get(Booking, 1).status == "booked"
        assert db.scalar(select(func.count()).select_from(Booking)) == 1
        assert db.scalar(select(func.count()).select_from(CountingSession)) == 0


@pytest.mark.parametrize("token", ["student", "unknown-role", "inactive"])
def test_staff_endpoint_rejects_disallowed_user_without_writes(api, token):
    client, factory = api
    response = client.post(
        STAFF_PATH, headers=headers(token), json={"initial_count": 3}
    )
    assert response.status_code == 403
    expected = "account_inactive" if token == "inactive" else "forbidden"
    assert response.json()["error"]["code"] == expected
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(CountingSession)) == 0


@pytest.mark.parametrize("token", ["librarian", "admin"])
def test_staff_and_admin_can_start_counting_session(api, token):
    client, factory = api
    response = client.post(
        STAFF_PATH, headers=headers(token), json={"initial_count": 3}
    )
    assert response.status_code == 201, response.text
    assert response.json()["initial_count"] == 3
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(CountingSession)) == 1


@pytest.mark.parametrize("method,path,body,status", [
    ("GET", "/api/v1/bookings/1", None, 404),
    ("DELETE", "/api/v1/bookings/1", None, 403),
    ("POST", "/api/v1/bookings/1/check-in-token", None, 403),
    ("POST", "/api/v1/check-in", {"booking_id": 1, "qr_token": "test-token"}, 403),
])
def test_student_cannot_access_another_users_booking(api, method, path, body, status):
    client, factory = api
    response = client.request(method, path, json=body, headers=headers("student"))
    assert response.status_code == status, response.text
    with factory() as db:
        booking = db.get(Booking, 1)
        assert booking.status == "booked"
        assert booking.checkin_at is None


def test_booking_list_only_shows_current_users_bookings(api):
    client, _ = api
    student = client.get("/api/v1/bookings", headers=headers("student"))
    assert student.status_code == 200, student.text
    assert student.json()["items"] == []
    owner = client.get("/api/v1/bookings/1", headers=headers("librarian"))
    assert owner.status_code == 200, owner.text
    assert owner.json()["user_id"] == 2


def test_require_roles_cannot_be_configured_without_roles():
    with pytest.raises(ValueError):
        require_roles()
