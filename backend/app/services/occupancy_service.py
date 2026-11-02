from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.occupancy_record import OccupancyRecord
from app.repositories import occupancy_repository
from app.schemas.occupancy import OccupancyObservationCreate


class RoomNotFoundError(Exception):
    pass


class OccupancyNotFoundError(Exception):
    pass


class ObservationConflictError(Exception):
    pass


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _same_observation(
    existing: OccupancyRecord, incoming: OccupancyObservationCreate
) -> bool:
    return (
        existing.room_id == incoming.room_id
        and existing.occupied_count == incoming.occupied_count
        and _as_utc(existing.observed_at) == incoming.observed_at
    )


def submit_observation(
    db: Session, incoming: OccupancyObservationCreate
) -> tuple[OccupancyRecord, bool]:
    if occupancy_repository.get_room(db, incoming.room_id) is None:
        raise RoomNotFoundError

    existing = occupancy_repository.get_by_observation_id(
        db, incoming.observation_id
    )
    if existing is not None:
        if _same_observation(existing, incoming):
            return existing, False
        raise ObservationConflictError

    record = OccupancyRecord(
        observation_id=incoming.observation_id,
        room_id=incoming.room_id,
        occupied_count=incoming.occupied_count,
        observed_at=incoming.observed_at,
        source="cv",
    )
    try:
        return occupancy_repository.create_observation(db, record), True
    except IntegrityError:
        # Two CV retries can arrive concurrently. Resolve the unique-key race
        # by checking the committed observation after rolling back this session.
        db.rollback()
        existing = occupancy_repository.get_by_observation_id(
            db, incoming.observation_id
        )
        if existing is not None:
            if _same_observation(existing, incoming):
                return existing, False
            raise ObservationConflictError from None
        if occupancy_repository.get_room(db, incoming.room_id) is None:
            raise RoomNotFoundError from None
        raise


def get_latest_observation(db: Session, room_id: int) -> OccupancyRecord:
    if occupancy_repository.get_room(db, room_id) is None:
        raise RoomNotFoundError

    record = occupancy_repository.get_latest_for_room(db, room_id)
    if record is None:
        raise OccupancyNotFoundError
    return record
