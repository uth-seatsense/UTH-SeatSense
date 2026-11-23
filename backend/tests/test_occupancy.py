from app.api.v1.endpoints import occupancy


def test_latest_occupancy_route_is_registered() -> None:
    assert any(
        route.path == "/rooms/{room_id}/latest" and "GET" in route.methods
        for route in occupancy.router.routes
    )


def test_current_occupancy_returns_latest_aggregated_count() -> None:
    from datetime import datetime, timezone

    from app.api.v1.endpoints.occupancy import get_current_occupancy

    observed_at = datetime(2026, 11, 4, 2, 0, tzinfo=timezone.utc)

    class Result:
        def mappings(self):
            return self

        def one(self):
            return {
                "current_count": 12,
                "updated_at": observed_at,
                "location": "Thư viện UTH",
            }

    class Database:
        def execute(self, query):
            assert "room_occupancy_status" in str(query)
            assert "auth_sessions" in str(query)
            return Result()

    response = get_current_occupancy(Database())

    assert response.model_dump() == {
        "current_count": 12,
        "updated_at": observed_at,
        "location": "Thư viện UTH",
        "web_logged_in_count": 0,
        "active_room_count": 0,
    }


def test_current_occupancy_without_records_returns_null_count() -> None:
    from app.api.v1.endpoints.occupancy import get_current_occupancy

    class Result:
        def mappings(self):
            return self

        def one(self):
            return {
                "current_count": None,
                "updated_at": None,
                "location": "Thư viện UTH",
            }

    class Database:
        def execute(self, query):
            return Result()

    response = get_current_occupancy(Database())
    assert response.current_count is None
    assert response.updated_at is None


def test_room_status_route_returns_room_and_web_login_counts() -> None:
    from datetime import datetime, timezone

    from app.api.v1.endpoints.occupancy import get_room_occupancy_status

    updated_at = datetime(2026, 11, 23, 4, 28, tzinfo=timezone.utc)

    class Result:
        def mappings(self):
            return self

        def all(self):
            return [{
                "room_id": 5,
                "room_code": "A101",
                "room_name": "Phòng đọc A101",
                "campus_code": "CS1",
                "campus_name": "Cơ sở 1",
                "capacity": 40,
                "capacity_confirmed": True,
                "current_count": 12,
                "available_seats": 28,
                "updated_at": updated_at,
            }]

        def one(self):
            return {"web_logged_in_count": 3}

    class Database:
        def __init__(self):
            self.call = 0

        def execute(self, query):
            self.call += 1
            return Result()

    response = get_room_occupancy_status(Database())
    assert response.total_rooms == 1
    assert response.total_people_in_rooms == 12
    assert response.web_logged_in_count == 3
    assert response.rooms[0].room_code == "A101"
