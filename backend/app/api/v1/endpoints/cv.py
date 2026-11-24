from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.errors import api_error
from app.db.session import get_db
from app.api.deps import require_cv_api_key
from app.models.room import Room
from app.schemas.count_event import CountEventCreate, CountEventReceipt
from app.repositories.cv_count_repository import CVRecordConflict
from app.schemas.cv_count import (
    CVCountBatch,
    CVCountBatchResponse,
    CVCountReceipt,
    ErrorEnvelope,
)
from app.services.cv_count_service import CVCountService
from app.services.cv_count_service import RoomNotFoundError
from app.services.occupancy_service import OccupancyService, CountEventConflictError

router = APIRouter()
cv_count_service = CVCountService()
occupancy_service = OccupancyService()


@router.post("/events", response_model=CountEventReceipt, status_code=201,
             dependencies=[Depends(require_cv_api_key)])
def receive_count_event(payload: CountEventCreate, db: Session = Depends(get_db)) -> CountEventReceipt:
    try:
        event, created = occupancy_service.receive_count_event(db, payload)
    except CountEventConflictError:
        raise api_error(409, "event_id_conflict", "event_id already exists with different content") from None
    except RoomNotFoundError:
        raise api_error(404, "room_not_found", "Room does not exist") from None
    return CountEventReceipt(event_id=event.event_id, room_id=event.room_id,
                             received_at=event.received_at, duplicate=not created)


@router.post(
    "/count-records",
    response_model=CVCountBatchResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_cv_api_key)],
    responses={
        400: {"model": ErrorEnvelope, "description": "Malformed JSON"},
        409: {"model": ErrorEnvelope, "description": "CV record conflict"},
        404: {"model": ErrorEnvelope, "description": "Unknown room code"},
        422: {"model": ErrorEnvelope, "description": "Invalid request"},
        503: {"model": ErrorEnvelope, "description": "Database unavailable"},
    },
)
def receive_cv_count_records(
    payload: CVCountBatch,
    db: Session = Depends(get_db),
) -> CVCountBatchResponse:
    try:
        saved = cv_count_service.save_many_with_status(
            payload.records, session=db
        )
    except CVRecordConflict:
        raise api_error(
            409,
            "cv_record_conflict",
            "A session/frame key already exists with different CV content",
        ) from None
    except RoomNotFoundError:
        raise api_error(
            404,
            "room_not_found",
            "A room code in the CV batch does not exist",
        ) from None
    except SQLAlchemyError:
        raise api_error(
            503,
            "database_unavailable",
            "The database is temporarily unavailable",
        ) from None

    records = [
        CVCountReceipt(
            record_id=record.id,
            session_id=record.session_id,
            frame_index=record.frame_index,
            room_code=record.room_code,
            room_id=record.room_id,
            received_at=record.received_at,
            duplicate=duplicate,
        )
        for record, duplicate in saved
    ]
    duplicate_count = sum(item.duplicate for item in records)
    return CVCountBatchResponse(
        created_count=len(records) - duplicate_count,
        duplicate_count=duplicate_count,
        records=records,
    )
