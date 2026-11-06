from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.occupancy_record import OccupancyRecord
from app.models.room import Room


def get_room(db: Session, room_id: int) -> Room | None:
    return db.get(Room, room_id)


def get_by_observation_id(db: Session, observation_id: UUID) -> OccupancyRecord | None:
    statement = select(OccupancyRecord).where(
        OccupancyRecord.observation_id == observation_id
    )
    return db.scalar(statement)


def create_observation(db: Session, record: OccupancyRecord) -> OccupancyRecord:
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_for_room(db: Session, room_id: int) -> OccupancyRecord | None:
    statement = (
        select(OccupancyRecord)
        .where(OccupancyRecord.room_id == room_id)
        .order_by(desc(OccupancyRecord.recorded_at), desc(OccupancyRecord.id))
        .limit(1)
    )
    return db.scalar(statement)
