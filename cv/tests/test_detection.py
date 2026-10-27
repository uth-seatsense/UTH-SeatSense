def test_detection_module_is_importable() -> None:
    from app.detection import detector

    assert detector is not None
