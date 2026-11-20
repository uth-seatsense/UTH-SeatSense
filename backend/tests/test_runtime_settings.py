import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Settings


def test_occupancy_thresholds_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OCCUPANCY_CROWDED_THRESHOLD", "0.75")
    monkeypatch.setenv("OCCUPANCY_STALE_SECONDS", "45")
    monkeypatch.setenv("DEVICE_OFFLINE_SECONDS", "120")

    settings = Settings(_env_file=None)

    assert settings.occupancy_crowded_threshold == 0.75
    assert settings.occupancy_stale_seconds == 45
    assert settings.device_offline_seconds == 120


def test_crowded_threshold_must_be_a_fraction() -> None:
    with pytest.raises(ValidationError):
        Settings(occupancy_crowded_threshold=1.1)
