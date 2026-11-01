from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.session import get_session_factory
from app.repositories.cv_count_repository import CVCountRepository
from app.schemas.cv_count import CVCountInput, CVCountRead


class RoomNotFoundError(Exception):
    pass


class OccupancyNotFoundError(Exception):
    pass


class CVCountService:
    def __init__(self, session_factory=None):
        # Resolve the application database lazily so importing the API does not
        # require a configured database or make a connection during startup.
        self.factory = session_factory

    def _factory(self):
        return self.factory if self.factory is not None else get_session_factory()

    def save(self, payload):
        return self.save_many([payload])[0]

    def save_many(self, payloads):
        return [record for record, _ in self.save_many_with_status(payloads)]

    def save_many_with_status(
        self, payloads, *, session: Session | None = None
    ) -> list[tuple[CVCountRead, bool]]:
        if not 1 <= len(payloads) <= 1000:
            raise ValueError('Batch must contain 1..1000 records')
        records = [CVCountInput.model_validate(item) for item in payloads]

        if session is not None:
            with session.begin():
                saved = self._save_validated(session, records)
        else:
            with self._factory().begin() as owned_session:
                saved = self._save_validated(owned_session, records)
        return [
            (CVCountRead.model_validate(record), duplicate)
            for record, duplicate in saved
        ]

    @staticmethod
    def _save_validated(session: Session, records: list[CVCountInput]):
        repository = CVCountRepository(session)
        return [repository.save(record) for record in records]

    def history(self, **filters):
        with self._factory()() as session:
            return [
                CVCountRead.model_validate(row)
                for row in CVCountRepository(session).history(**filters)
            ]

    def latest(self, **filters):
        if 'limit' in filters or 'offset' in filters:
            raise ValueError('latest does not accept pagination')
        records = self.history(**filters, limit=1)
        return records[0] if records else None

    def latest_live_for_room(self, session: Session, room_id: int) -> CVCountRead:
        repository = CVCountRepository(session)
        if repository.get_room(room_id) is None:
            raise RoomNotFoundError
        record = repository.get_latest_webcam_for_room(room_id)
        if record is None:
            raise OccupancyNotFoundError
        return CVCountRead.model_validate(record)


def is_stale(received_at: datetime, *, now: datetime | None = None) -> bool:
    current_time = now or datetime.now(timezone.utc)
    timestamp = received_at
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return current_time.astimezone(timezone.utc) - timestamp.astimezone(
        timezone.utc
    ) > timedelta(seconds=30)
