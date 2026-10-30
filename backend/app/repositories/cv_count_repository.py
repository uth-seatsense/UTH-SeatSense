from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.cv_count_record import CVCountRecord
from app.models.room import Room


class CVRecordConflict(ValueError):
    """Same session/frame was already persisted with different CV content."""


class CVCountRepository:
    def __init__(self, session):
        self.session = session

    def save(self, payload):
        values = payload.model_dump()
        values['room_code'] = values.pop('room_id')
        values['room_id'] = self.session.scalar(select(Room.id).where(Room.code == values['room_code'])) if values['room_code'] is not None else None
        statement = insert(CVCountRecord).values(**values).on_conflict_do_nothing(
            constraint='uq_cv_session_frame').returning(CVCountRecord.id)
        identity = self.session.scalar(statement)
        if identity is not None:
            return self.session.get(CVCountRecord, identity)
        existing = self.session.scalar(select(CVCountRecord).where(
            CVCountRecord.session_id == payload.session_id,
            CVCountRecord.frame_index == payload.frame_index))
        # Mapping is receipt metadata: retry does not remap or overwrite old rows.
        if any(getattr(existing,key) != value for key,value in values.items() if key != 'room_id'):
            raise CVRecordConflict('Session/frame already exists with different content')
        return existing

    def history(self, *, camera_id=None, room_id=None, room_code=None, session_id=None,
                start=None, end=None, limit=100, offset=0):
        if not isinstance(limit,int) or not 1 <= limit <= 500 or not isinstance(offset,int) or offset < 0:
            raise ValueError('limit must be 1..500 and offset nonnegative')
        for instant in (start,end):
            if instant is not None and (not isinstance(instant,datetime) or instant.utcoffset() is None):
                raise ValueError('Query timestamps require a timezone')
        if start is not None and end is not None and start >= end:
            raise ValueError('start must be earlier than end')
        statement = select(CVCountRecord)
        for key,value in dict(camera_id=camera_id,room_id=room_id,room_code=room_code,session_id=session_id).items():
            if value is not None:
                statement = statement.where(getattr(CVCountRecord,key) == value)
        if start is not None:
            statement = statement.where(CVCountRecord.recorded_at >= start.astimezone(timezone.utc))
        if end is not None:
            statement = statement.where(CVCountRecord.recorded_at < end.astimezone(timezone.utc))
        return self.session.scalars(statement.order_by(CVCountRecord.recorded_at.desc(),CVCountRecord.id.desc()).limit(limit).offset(offset)).all()
