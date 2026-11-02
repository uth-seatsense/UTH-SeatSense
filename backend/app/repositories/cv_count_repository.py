from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models.cv_count_record import CVCountRecord
from app.models.room import Room
from app.schemas.cv_count import CVCountInput


class CVRecordConflict(ValueError):
    """A session/frame key was already stored with different CV content."""


class CVCountRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_room(self, room_id: int) -> Room | None:
        return self.session.get(Room, room_id)

    def save(self, payload: CVCountInput) -> tuple[CVCountRecord, bool]:
        values = payload.model_dump()
        values['room_code'] = values.pop('room_id')
        values['room_id'] = (
            self.session.scalar(
                select(Room.id).where(Room.code == values['room_code'])
            )
            if values['room_code'] is not None
            else None
        )

        dialect = self.session.get_bind().dialect.name
        if dialect == 'postgresql':
            insert = postgres_insert
        elif dialect == 'sqlite':
            insert = sqlite_insert
        else:
            raise RuntimeError(f'Unsupported database dialect: {dialect}')

        statement = (
            insert(CVCountRecord)
            .values(**values)
            .on_conflict_do_nothing(
                index_elements=[CVCountRecord.session_id, CVCountRecord.frame_index]
            )
            .returning(CVCountRecord.id)
        )
        identity = self.session.scalar(statement)
        if identity is not None:
            record = self.session.get(CVCountRecord, identity)
            if record is None:  # pragma: no cover - guarded by INSERT RETURNING
                raise RuntimeError('Inserted CV record could not be reloaded')
            return record, False

        existing = self.session.scalar(
            select(CVCountRecord).where(
                CVCountRecord.session_id == payload.session_id,
                CVCountRecord.frame_index == payload.frame_index,
            )
        )
        if existing is None:  # pragma: no cover - unique conflict must expose a row
            raise RuntimeError('CV record conflict row could not be loaded')

        # Room mapping is receipt metadata. A retry never rewrites an older FK
        # if the room code was mapped after its first receipt.
        content = {key: value for key, value in values.items() if key != 'room_id'}
        for key, value in content.items():
            stored_value = getattr(existing, key)
            if isinstance(value, datetime):
                if stored_value.tzinfo is None or stored_value.utcoffset() is None:
                    stored_value = stored_value.replace(tzinfo=timezone.utc)
                else:
                    stored_value = stored_value.astimezone(timezone.utc)
                value = value.astimezone(timezone.utc)
            if stored_value != value:
                raise CVRecordConflict(
                    'Session/frame already exists with different CV content'
                )
        return existing, True

    def get_latest_webcam_for_room(self, room_id: int) -> CVCountRecord | None:
        statement = (
            select(CVCountRecord)
            .where(
                CVCountRecord.room_id == room_id,
                CVCountRecord.source_type == 'webcam',
            )
            .order_by(desc(CVCountRecord.recorded_at), desc(CVCountRecord.id))
            .limit(1)
        )
        return self.session.scalar(statement)

    def history(
        self,
        *,
        camera_id=None,
        room_id=None,
        room_code=None,
        session_id=None,
        start=None,
        end=None,
        limit=100,
        offset=0,
    ):
        if (
            not isinstance(limit, int)
            or not 1 <= limit <= 500
            or not isinstance(offset, int)
            or offset < 0
        ):
            raise ValueError('limit must be 1..500 and offset nonnegative')
        for instant in (start, end):
            if instant is not None and (
                not isinstance(instant, datetime) or instant.utcoffset() is None
            ):
                raise ValueError('Query timestamps require a timezone')
        if start is not None and end is not None and start >= end:
            raise ValueError('start must be earlier than end')

        statement = select(CVCountRecord)
        for key, value in dict(
            camera_id=camera_id,
            room_id=room_id,
            room_code=room_code,
            session_id=session_id,
        ).items():
            if value is not None:
                statement = statement.where(getattr(CVCountRecord, key) == value)
        if start is not None:
            statement = statement.where(
                CVCountRecord.recorded_at >= start.astimezone(timezone.utc)
            )
        if end is not None:
            statement = statement.where(
                CVCountRecord.recorded_at < end.astimezone(timezone.utc)
            )
        return self.session.scalars(
            statement.order_by(
                CVCountRecord.recorded_at.desc(), CVCountRecord.id.desc()
            )
            .limit(limit)
            .offset(offset)
        ).all()
