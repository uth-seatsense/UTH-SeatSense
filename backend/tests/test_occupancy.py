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
            assert "DISTINCT ON (occupancy.room_id)" in str(query)
            assert "rooms.is_active IS TRUE" in str(query)
            return Result()

    response = get_current_occupancy(Database())

    assert response.model_dump() == {
        "current_count": 12,
        "updated_at": observed_at,
        "location": "Thư viện UTH",
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
