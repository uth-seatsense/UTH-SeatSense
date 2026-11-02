from app.api.v1.endpoints import occupancy


def test_latest_occupancy_route_is_registered() -> None:
    assert any(
        route.path == "/rooms/{room_id}/latest" and "GET" in route.methods
        for route in occupancy.router.routes
    )
