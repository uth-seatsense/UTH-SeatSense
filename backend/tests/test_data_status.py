from datetime import datetime, timedelta, timezone
import pytest
from app.services.occupancy_service import OccupancyService
from app.core.config import settings


class TestDataStatusCalculation:
    """Test data status calculation based on recorded_at and device_status."""

    def test_fresh_data_with_online_device(self):
        """Data is fresh when recent and device is online."""
        now = datetime.now(timezone.utc)
        recent_time = now - timedelta(seconds=10)

        status = OccupancyService.calculate_data_status(recent_time, "online")

        assert status == "fresh"

    def test_fresh_data_within_stale_threshold(self):
        """Data is fresh when within stale threshold (default 30s)."""
        now = datetime.now(timezone.utc)
        just_before_stale = now - timedelta(seconds=settings.occupancy_stale_seconds - 1)

        status = OccupancyService.calculate_data_status(just_before_stale, "online")

        assert status == "fresh"

    def test_stale_data_exceeds_stale_threshold(self):
        """Data is stale when exceeding stale threshold but not disconnected."""
        now = datetime.now(timezone.utc)
        stale_time = now - timedelta(seconds=settings.occupancy_stale_seconds + 10)

        status = OccupancyService.calculate_data_status(stale_time, "online")

        assert status == "stale"

    def test_stale_data_between_thresholds(self):
        """Data is stale when between stale and disconnected thresholds."""
        now = datetime.now(timezone.utc)
        # Between 30s (stale) and 90s (disconnected)
        between_time = now - timedelta(seconds=60)

        status = OccupancyService.calculate_data_status(between_time, "online")

        assert status == "stale"

    def test_disconnected_exceeds_offline_threshold(self):
        """Data is disconnected when exceeding offline threshold (default 90s)."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(seconds=settings.device_offline_seconds + 10)

        status = OccupancyService.calculate_data_status(old_time, "online")

        assert status == "disconnected"

    def test_disconnected_device_offline_status(self):
        """Data is disconnected when device_status is 'offline'."""
        now = datetime.now(timezone.utc)
        recent_time = now - timedelta(seconds=5)

        status = OccupancyService.calculate_data_status(recent_time, "offline")

        assert status == "disconnected"

    def test_disconnected_device_error_status(self):
        """Data is disconnected when device_status is 'error'."""
        now = datetime.now(timezone.utc)
        recent_time = now - timedelta(seconds=5)

        status = OccupancyService.calculate_data_status(recent_time, "error")

        assert status == "disconnected"

    def test_none_when_no_recorded_at(self):
        """Status is None when recorded_at is None."""
        status = OccupancyService.calculate_data_status(None, "online")

        assert status is None

    def test_fresh_when_device_status_none(self):
        """Data is fresh when device_status is None but time is recent."""
        now = datetime.now(timezone.utc)
        recent_time = now - timedelta(seconds=10)

        status = OccupancyService.calculate_data_status(recent_time, None)

        assert status == "fresh"

    def test_exact_stale_threshold_boundary(self):
        """Data at exact stale threshold is considered stale."""
        now = datetime.now(timezone.utc)
        exact_threshold = now - timedelta(seconds=settings.occupancy_stale_seconds)

        status = OccupancyService.calculate_data_status(exact_threshold, "online")

        assert status == "stale"

    def test_exact_disconnected_threshold_boundary(self):
        """Data at exact disconnected threshold is considered disconnected."""
        now = datetime.now(timezone.utc)
        exact_threshold = now - timedelta(seconds=settings.device_offline_seconds)

        status = OccupancyService.calculate_data_status(exact_threshold, "online")

        assert status == "disconnected"

    def test_device_status_overrides_time_threshold(self):
        """Device offline status overrides fresh time threshold."""
        now = datetime.now(timezone.utc)
        very_recent = now - timedelta(seconds=1)

        status = OccupancyService.calculate_data_status(very_recent, "offline")

        assert status == "disconnected"
