from datetime import datetime, timezone

from sqlalchemy import Boolean, and_, case, func, literal_column, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.campus import Campus
from app.models.count_event import CountEvent
from app.models.counting_session import CountingSession
from app.models.cv_count_record import CVCountRecord
from app.models.occupancy_record import OccupancyRecord
from app.models.room import Room


class CountEventConflictError(Exception):
    pass


class RoomNotFoundError(Exception):
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
    def start_counting_session(
        db: Session, room_id: int, initial_count: int, user_id: int
    ) -> CountingSession:
        # Serialize transitions for this room while closing the previous session.
        room = db.scalar(
            select(Room.id)
            .where(Room.id == room_id, Room.is_active.is_(True))
            .with_for_update()
        )
        if room is None:
            raise RoomNotFoundError

        started_at = datetime.now(timezone.utc)
        previous = db.scalar(
            select(CountingSession).where(
                CountingSession.room_id == room_id,
                CountingSession.ended_at.is_(None),
            )
        )
        if previous is not None:
            previous.ended_at = started_at
            db.flush()

        session = CountingSession(
            room_id=room_id,
            initial_count=initial_count,
            started_by=user_id,
            started_at=started_at,
        )
        db.add(session)
        db.commit()
        return session

    @staticmethod
    def current_room_counts(
        db: Session, *, room_id: int | None = None, campus: str | None = None
    ) -> list[dict]:
        now = datetime.now(timezone.utc)
        # The capacity fixture migration manages this column separately from the Room ORM.
        capacity_confirmed = literal_column("rooms.capacity_confirmed", Boolean)
        delta = case(
            (CountEvent.direction == "in", 1),
            (CountEvent.direction == "out", -1),
            else_=0,
        )
        last_cv_seen = (
            select(func.max(CVCountRecord.received_at))
            .where(
                CVCountRecord.room_id == Room.id,
                CVCountRecord.source_type == "webcam",
                CVCountRecord.received_at >= CountingSession.started_at,
            )
            .correlate(Room, CountingSession)
            .scalar_subquery()
        )
        # The CV session_id identifies the sender, which can restart mid-session.
        # Assign events to the operator's room session using the occurrence time.
        query = (
            select(
                Room.id.label("room_id"),
                Room.code.label("room_code"),
                Room.name.label("room_name"),
                Campus.code.label("campus_code"),
                Campus.name.label("campus_name"),
                Room.capacity,
                capacity_confirmed.label("capacity_confirmed"),
                CountingSession.initial_count,
                CountingSession.started_at,
                func.sum(delta).label("net_count"),
                func.max(CountEvent.event_time).label("last_event_at"),
                last_cv_seen.label("last_cv_seen_at"),
            )
            .outerjoin(Campus, Campus.campus_id == Room.campus_id)
            .outerjoin(
                CountingSession,
                and_(
                    CountingSession.room_id == Room.id,
                    CountingSession.ended_at.is_(None),
                ),
            )
            .outerjoin(
                CountEvent,
                and_(
                    CountEvent.room_id == Room.id,
                    CountEvent.event_time >= CountingSession.started_at,
                    CountEvent.event_time <= now,
                    CountEvent.device_status == "online",
                ),
            )
            .where(Room.is_active.is_(True))
            .group_by(
                Room.id,
                Room.code,
                Room.name,
                Campus.code,
                Campus.name,
                Room.capacity,
                capacity_confirmed,
                CountingSession.initial_count,
                CountingSession.started_at,
            )
            .order_by(Room.id)
        )
        if room_id is not None:
            query = query.where(Room.id == room_id)
        if campus is not None:
            query = query.where(Campus.code == campus)

        rooms = []
        for row in db.execute(query).mappings():
            current_count = available_seats = None
            over_capacity = underflow = None
            observed_at = updated_at = None
            #seat 93
            if row.initial_count is not None and row.capacity_confirmed:
                total = row.initial_count + row.net_count
                current_count = max(0, total)
                available_seats = max(0, row.capacity - current_count)
                over_capacity = current_count > row.capacity
                underflow = total < 0
                observed_at = _as_utc(row.last_event_at or row.started_at)
                updated_at = max(observed_at, _as_utc(row.last_cv_seen_at or row.started_at))
            rooms.append(
                {
                    "room_id": row.room_id,
                    "room_code": row.room_code,
                    "room_name": row.room_name,
                    "campus_code": row.campus_code,
                    "campus_name": row.campus_name,
                    "capacity": row.capacity,
                    "capacity_confirmed": row.capacity_confirmed,
                    "current_count": current_count,
                    "available_seats": available_seats,
                    "over_capacity": over_capacity,
                    "underflow": underflow,
                    "observed_at": observed_at,
                    "updated_at": updated_at,
                }
            )
        return rooms

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

    @staticmethod
    def calculate_data_status(
        recorded_at: datetime | None,
        device_status: str | None = None
    ) -> str | None:
        """
        Calculate data freshness status based on recorded_at timestamp and device_status.

        Returns:
            - "fresh": data is recent and device is online
            - "stale": data exceeds stale threshold
            - "disconnected": data exceeds disconnected threshold or device is offline/error
            - None: no data available
        """
        if recorded_at is None:
            return None

        now = datetime.now(timezone.utc)
        age_seconds = (now - recorded_at).total_seconds()

        # Device explicitly offline or error -> disconnected
        if device_status in ("offline", "error"):
            return "disconnected"

        # Check time-based thresholds
        if age_seconds >= settings.device_offline_seconds:
            return "disconnected"
        elif age_seconds >= settings.occupancy_stale_seconds:
            return "stale"
        else:
            return "fresh"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
