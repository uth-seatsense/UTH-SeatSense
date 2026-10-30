"""Transactional persistence, reusable by future API endpoints/import workers."""
from app.db.session import get_session_factory
from app.schemas.cv_count import CVCountInput, CVCountRead
from app.repositories.cv_count_repository import CVCountRepository


class CVCountService:
    def __init__(self, session_factory=None):
        self.factory = session_factory if session_factory is not None else get_session_factory()

    def save(self, payload):
        return self.save_many([payload])[0]

    def save_many(self, payloads):
        if not 1 <= len(payloads) <= 1000:
            raise ValueError('Batch must contain 1..1000 records')
        records = [CVCountInput.model_validate(item) for item in payloads]
        with self.factory.begin() as session:
            repository = CVCountRepository(session)
            return [CVCountRead.model_validate(repository.save(item)) for item in records]

    def history(self, **filters):
        with self.factory() as session:
            return [CVCountRead.model_validate(row) for row in CVCountRepository(session).history(**filters)]

    def latest(self, **filters):
        if 'limit' in filters or 'offset' in filters:
            raise ValueError('latest does not accept pagination')
        records = self.history(**filters,limit=1)
        return records[0] if records else None
