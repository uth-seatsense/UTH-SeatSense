def test_reservations_endpoint_module_is_importable() -> None:
    from app.api.v1.endpoints import reservations

    assert reservations.router is not None
