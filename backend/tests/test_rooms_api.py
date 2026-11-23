"""
Tests for Rooms API endpoints - SEAT-56
Tests GET /api/v1/rooms and GET /api/v1/rooms/{room_id}
"""
import pytest
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
from app.models.user import User


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

    # Create test user for authentication
    test_user = User(
        email="test@ut.edu.vn",
        display_name="Test User",
        password_hash="dummy_hash",
        role="student",
        is_active=True,
    )
    db.add(test_user)

    # Create test campuses
    cs1 = Campus(code="CS1", name="Cơ sở 1", is_active=True)
    cs3 = Campus(code="CS3", name="Cơ sở 3", is_active=True)
    db.add_all([cs1, cs3])
    db.commit()
    db.refresh(cs1)
    db.refresh(cs3)

    # Create test rooms
    rooms = [
        Room(
            code="A101",
            name="Phòng A101",
            room_type="free_area",
            capacity=50,
            campus_id=cs1.campus_id,
            building="Cơ sở 1",
            location="Tầng 1",
            status="active",
            is_active=True,
        ),
        Room(
            code="A201",
            name="Phòng A201",
            room_type="topic_room",
            capacity=10,
            campus_id=cs1.campus_id,
            building="Cơ sở 1",
            location="Tầng 2",
            status="active",
            is_active=True,
        ),
        Room(
            code="B101",
            name="Phòng B101",
            room_type="free_area",
            capacity=40,
            campus_id=cs3.campus_id,
            building="Cơ sở 3",
            location="Tầng 1",
            status="active",
            is_active=True,
        ),
        Room(
            code="C101",
            name="Phòng C101 - Bảo trì",
            room_type="free_area",
            capacity=30,
            campus_id=cs1.campus_id,
            building="Cơ sở 1",
            location="Tầng 3",
            status="maintenance",
            is_active=True,
        ),
    ]
    db.add_all(rooms)
    db.commit()

    yield

    Base.metadata.drop_all(bind=engine)
    db.close()


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    # In real implementation, you would get a valid token
    # For now, we'll mock the get_current_user dependency
    from app.api.deps import get_current_user

    def mock_user():
        return User(
            user_id=1,
            email="test@ut.edu.vn",
            display_name="Test User",
            role="student",
        )

    app.dependency_overrides[get_current_user] = mock_user
    yield {"Authorization": "Bearer mock_token"}
    app.dependency_overrides.pop(get_current_user, None)


def test_list_rooms_success(auth_headers):
    """Test GET /api/v1/rooms - should return list of active rooms"""
    response = client.get("/api/v1/rooms", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "limit" in data
    assert "offset" in data
    assert "total" in data

    # Should return only active rooms (status='active')
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["limit"] == 50
    assert data["offset"] == 0


def test_list_rooms_filter_by_campus_cs1(auth_headers):
    """Test GET /api/v1/rooms?campus_code=CS1 - filter by CS1"""
    response = client.get("/api/v1/rooms?campus_code=CS1", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2  # A101, A201 (C101 is maintenance)
    for room in data["items"]:
        assert room["campus_code"] == "CS1"


def test_list_rooms_filter_by_campus_cs3(auth_headers):
    """Test GET /api/v1/rooms?campus_code=CS3 - filter by CS3"""
    response = client.get("/api/v1/rooms?campus_code=CS3", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1  # B101
    assert data["items"][0]["campus_code"] == "CS3"
    assert data["items"][0]["code"] == "B101"


def test_list_rooms_filter_by_room_type_free_area(auth_headers):
    """Test GET /api/v1/rooms?room_type=free_area - filter by free_area"""
    response = client.get("/api/v1/rooms?room_type=free_area", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2  # A101, B101
    for room in data["items"]:
        assert room["room_type"] == "free_area"


def test_list_rooms_filter_by_room_type_topic_room(auth_headers):
    """Test GET /api/v1/rooms?room_type=topic_room - filter by topic_room"""
    response = client.get("/api/v1/rooms?room_type=topic_room", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1  # A201
    assert data["items"][0]["room_type"] == "topic_room"
    assert data["items"][0]["code"] == "A201"


def test_list_rooms_pagination(auth_headers):
    """Test GET /api/v1/rooms?limit=2&offset=0 - pagination"""
    response = client.get("/api/v1/rooms?limit=2&offset=0", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["total"] == 3
    assert len(data["items"]) == 2


def test_list_rooms_pagination_offset(auth_headers):
    """Test GET /api/v1/rooms?limit=2&offset=2 - second page"""
    response = client.get("/api/v1/rooms?limit=2&offset=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["limit"] == 2
    assert data["offset"] == 2
    assert data["total"] == 3
    assert len(data["items"]) == 1  # Only 1 room left


def test_get_room_by_id_success(auth_headers):
    """Test GET /api/v1/rooms/{room_id} - get specific room"""
    # Get room list first to get valid room_id
    list_response = client.get("/api/v1/rooms", headers=auth_headers)
    rooms = list_response.json()["items"]
    test_room_id = rooms[0]["id"]

    response = client.get(f"/api/v1/rooms/{test_room_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_room_id
    assert "code" in data
    assert "name" in data
    assert "room_type" in data
    assert "capacity" in data
    assert "campus_code" in data
    assert "is_active" in data


def test_get_room_by_id_not_found(auth_headers):
    """Test GET /api/v1/rooms/999999 - room does not exist"""
    response = client.get("/api/v1/rooms/999999", headers=auth_headers)

    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert data["error"]["code"] == "room_not_found"


def test_get_room_invalid_id(auth_headers):
    """Test GET /api/v1/rooms/0 - invalid room_id"""
    response = client.get("/api/v1/rooms/0", headers=auth_headers)

    assert response.status_code == 422  # Validation error


def test_list_rooms_without_auth():
    """Test GET /api/v1/rooms without authentication - should return 401"""
    response = client.get("/api/v1/rooms")

    assert response.status_code == 401
