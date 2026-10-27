def test_occupancy_endpoint_module_is_importable() -> None:
    from app.api.v1.endpoints import occupancy

    assert occupancy.router is not None
