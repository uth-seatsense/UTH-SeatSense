import pytest
from app.core.config import settings
from app.services.occupancy_service import OccupancyService


class FakeRepo:
    def __init__(self):
        self.saved = None

    def save(self, record):
        self.saved = record


@pytest.fixture
def service():
    repo = FakeRepo()
    return OccupancyService(occupancy_repo=repo), repo


def test_tinh_so_nguoi_duong(service):
    svc, repo = service
    result = svc.calculate_occupancy(room_id=1, capacity=40, entries=25, exits=5)
    assert result["current_count"] == 20
    assert result["available_seats"] == 20
    assert result["over_capacity"] is False
    assert result["warning"] is False


def test_so_am_kep_ve_0(service):
    svc, repo = service
    result = svc.calculate_occupancy(room_id=1, capacity=40, entries=5, exits=10)
    assert result["current_count"] == 0
    assert result["warning"] is True


def test_vuot_suc_chua(service):
    svc, repo = service
    result = svc.calculate_occupancy(room_id=1, capacity=40, entries=45, exits=0)
    assert result["current_count"] == 45
    assert result["available_seats"] == 0
    assert result["over_capacity"] is True


def test_nguong_dong(service):
    svc, repo = service
    result = svc.calculate_occupancy(room_id=1, capacity=100, entries=75, exits=0)
    assert result["occupancy_level"] == "dong"

    result = svc.calculate_occupancy(room_id=1, capacity=100, entries=50, exits=0)
    assert result["occupancy_level"] == "vua"

    result = svc.calculate_occupancy(room_id=1, capacity=100, entries=20, exits=0)
    assert result["occupancy_level"] == "vang"


def test_vuot_suc_chua_45_vao_40_suc_chua(service):
    svc, repo = service
    result = svc.calculate_occupancy(room_id=1, capacity=40, entries=45, exits=0)
    assert result["current_count"] == 45
    assert result["available_seats"] == 0
    assert result["over_capacity"] is True
    assert result["occupancy_level"] == "dong"
