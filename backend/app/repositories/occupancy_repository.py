from app.models.occupancy_record import OccupancyRecord


class OccupancyRepository:
    def __init__(self, session=None):
        self.session = session

    def save(self, record: OccupancyRecord) -> OccupancyRecord:
        raise NotImplementedError("Chua trien khai DB session")

    def get_latest_by_room(self, room_id: int):
        raise NotImplementedError("Chua trien khai DB session")
