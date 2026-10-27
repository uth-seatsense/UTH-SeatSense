def test_counting_modules_are_importable() -> None:
    from app.counting import line_counter, occupancy

    assert line_counter is not None
    assert occupancy is not None
