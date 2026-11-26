from app.core.config import settings
from app.models.occupancy_record import OccupancyRecord
from app.models.count_event import CountEvent
from app.models.room import Room
from app.services.cv_count_service import RoomNotFoundError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class CountEventConflictError(Exception):
    pass


class OccupancyService:
    def __init__(self, occupancy_repo=None, room_repo=None):
        self.occupancy_repo = occupancy_repo
        self.room_repo = room_repo

    def calculate_occupancy(
        self,
        room_id: int,
        capacity: int,
        entries: int,
        exits: int,
        record_time=None,
    ) -> dict:
        from datetime import datetime, timezone

        raw_count = entries - exits
        warning = False
        if raw_count < 0:
            raw_count = 0
            warning = True

        available_seats = max(capacity - raw_count, 0)
        over_capacity = raw_count > capacity

        ratio = raw_count / capacity if capacity else 0.0
        if ratio <= settings.occupancy_low_threshold:
            level = "vang"
        elif ratio <= settings.occupancy_high_threshold:
            level = "vua"
        else:
            level = "dong"

        record = None
        if self.occupancy_repo:
            record = OccupancyRecord(
                room_id=room_id,
                current_count=raw_count,
                available_seats=available_seats,
                over_capacity=over_capacity,
                occupancy_level=level,
                source="cv",
                recorded_at=record_time or datetime.now(timezone.utc),
            )
            self.occupancy_repo.save(record)

        return {
            "room_id": room_id,
            "current_count": raw_count,
            "available_seats": available_seats,
            "over_capacity": over_capacity,
            "occupancy_level": level,
            "warning": warning,
            "recorded_at": str(record.recorded_at) if record else None,
        }

    @staticmethod
    def receive_count_event(db: Session, incoming) -> tuple:
        if db.get(Room, incoming.room_id) is None:
            raise RoomNotFoundError
        existing = db.get(CountEvent, incoming.event_id)
        if existing is not None:
            same = (
                existing.session_id == incoming.session_id
                and existing.room_id == incoming.room_id
                and existing.device_id == incoming.device_id
                and existing.direction == incoming.direction
                and _as_utc(existing.event_time) == incoming.event_time
                and existing.device_status == incoming.device_status
            )
            if same:
                return existing, False
            raise CountEventConflictError
        event = CountEvent(
            event_id=incoming.event_id,
            session_id=incoming.session_id,
            device_id=incoming.device_id,
            device_status=incoming.device_status,
            room_id=incoming.room_id,
            direction=incoming.direction,
            event_time=incoming.event_time,
            source="cv",
        )
        db.add(event)
        try:
            db.commit()
            db.refresh(event)
            return event, True
        except IntegrityError:
            db.rollback()
            existing = db.get(CountEvent, incoming.event_id)
            if existing is None:
                raise
            same = (
                existing.session_id == incoming.session_id
                and existing.room_id == incoming.room_id
                and existing.device_id == incoming.device_id
                and existing.direction == incoming.direction
                and _as_utc(existing.event_time) == incoming.event_time
                and existing.device_status == incoming.device_status
            )
            if same:
                return existing, False
            raise CountEventConflictError from None

    def get_room_occupancy(self, room_id: int):
        if self.occupancy_repo:
            return self.occupancy_repo.get_latest_by_room(room_id)
        return None


def _as_utc(value):
    from datetime import timezone
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
