def test_checkin_endpoint_module_is_importable() -> None:
    from app.api.v1.endpoints import checkin

    assert checkin.router is not None
