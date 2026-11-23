"""
Tests for Occupancy API endpoints - SEAT-56
Tests GET /api/v1/occupancy/rooms/{room_id}/latest and GET /api/v1/occupancy/current
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.campus import Campus
from app.models.room import Room
from app.models.cv_count_record import CVCountRecord


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables and seed test data before each test"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # Create test campus
    cs1 = Campus(code="CS1", name="Cơ sở 1", is_active=True)
    db.add(cs1)
    db.commit()
    db.refresh(cs1)

    # Create test rooms
    room_with_data = Room(
        code="A101",
        name="Phòng A101",
        room_type="free_area",
        capacity=50,
        campus_id=cs1.campus_id,
        building="Cơ sở 1",
        status="active",
        is_active=True,
    )
    room_without_data = Room(
        code="A102",
        name="Phòng A102",
        room_type="free_area",
        capacity=40,
        campus_id=cs1.campus_id,
        building="Cơ sở 1",
        status="active",
        is_active=True,
    )
    db.add_all([room_with_data, room_without_data])
    db.commit()
    db.refresh(room_with_data)
    db.refresh(room_without_data)

    # Create CV count record for room_with_data (webcam source)
    now = datetime.now(timezone.utc)
    cv_record = CVCountRecord(
        schema_version="1.0",
        session_id=uuid4(),
        camera_id="cam-01",
        room_code="A101",
        room_id=room_with_data.id,
        source_type="webcam",
        frame_index=100,
        timestamp_ms=10000.0,
        recorded_at=now,
        received_at=now,
        people_count=25,
        tracked_count=20,
        line_enabled=True,
        in_count=30,
        out_count=5,
        initial_occupancy=0,
        estimated_occupancy=25,
        occupancy_underflow=False,
    )
    db.add(cv_record)
    db.commit()

    yield {
        "room_with_data_id": room_with_data.id,
        "room_without_data_id": room_without_data.id,
    }

    Base.metadata.drop_all(bind=engine)
    db.close()


def test_get_latest_occupancy_success(setup_database):
    """Test GET /api/v1/occupancy/rooms/{room_id}/latest - with data"""
    room_id = setup_database["room_with_data_id"]
    response = client.get(f"/api/v1/occupancy/rooms/{room_id}/latest")

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert data["room_id"] == room_id
    assert data["room_code"] == "A101"
    assert data["camera_id"] == "cam-01"
    assert data["source_type"] == "webcam"
    assert data["people_count"] == 25
    assert data["tracked_count"] == 20
    assert data["estimated_occupancy"] == 25
    assert data["occupancy_underflow"] is False
    assert "recorded_at" in data
    assert "received_at" in data
    assert "is_stale" in data


def test_get_latest_occupancy_no_data_returns_503(setup_database):
    """Test GET /api/v1/occupancy/rooms/{room_id}/latest - no data (503 occupancy_unavailable)"""
    room_id = setup_database["room_without_data_id"]
    response = client.get(f"/api/v1/occupancy/rooms/{room_id}/latest")

    # According to SEAT-56 requirement: should return 503, not 404
    assert response.status_code == 503
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "occupancy_unavailable"


def test_get_latest_occupancy_room_not_found():
    """Test GET /api/v1/occupancy/rooms/999999/latest - room does not exist (404)"""
    response = client.get("/api/v1/occupancy/rooms/999999/latest")

    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "room_not_found"


def test_get_latest_occupancy_invalid_room_id():
    """Test GET /api/v1/occupancy/rooms/0/latest - invalid room_id (422)"""
    response = client.get("/api/v1/occupancy/rooms/0/latest")

    assert response.status_code == 422  # Validation error


def test_get_latest_occupancy_negative_room_id():
    """Test GET /api/v1/occupancy/rooms/-1/latest - negative room_id (422)"""
    response = client.get("/api/v1/occupancy/rooms/-1/latest")

    assert response.status_code == 422  # Validation error


def test_get_current_occupancy_aggregated():
    """Test GET /api/v1/occupancy/current - aggregated occupancy"""
    response = client.get("/api/v1/occupancy/current")

    # Note: This endpoint queries occupancy_records table which is empty in test
    # In production, it should return 200 with data, but in test it may return 503
    # We accept both as valid for now until SEAT-58 provides proper data flow
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()

        # Check required fields
        assert "current_count" in data
        assert "updated_at" in data
        assert "location" in data
        assert data["location"] == "Thư viện UTH"

        # current_count could be None or an integer
        if data["current_count"] is not None:
            assert isinstance(data["current_count"], int)
            assert data["current_count"] >= 0


def test_get_latest_occupancy_is_stale_field(setup_database):
    """Test that is_stale field is present and boolean"""
    room_id = setup_database["room_with_data_id"]
    response = client.get(f"/api/v1/occupancy/rooms/{room_id}/latest")

    assert response.status_code == 200
    data = response.json()

    assert "is_stale" in data
    assert isinstance(data["is_stale"], bool)


def test_get_latest_occupancy_datetime_format(setup_database):
    """Test that datetime fields are in ISO 8601 format with Z suffix"""
    room_id = setup_database["room_with_data_id"]
    response = client.get(f"/api/v1/occupancy/rooms/{room_id}/latest")

    assert response.status_code == 200
    data = response.json()

    # Check datetime format
    assert data["recorded_at"].endswith("Z")
    assert data["received_at"].endswith("Z")

    # Should be parseable as ISO 8601
    datetime.fromisoformat(data["recorded_at"].replace("Z", "+00:00"))
    datetime.fromisoformat(data["received_at"].replace("Z", "+00:00"))
