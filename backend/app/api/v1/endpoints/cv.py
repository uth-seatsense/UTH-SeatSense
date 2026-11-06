from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.errors import api_error
from app.db.session import get_db
from app.repositories.cv_count_repository import CVRecordConflict
from app.schemas.cv_count import (
    CVCountBatch,
    CVCountBatchResponse,
    CVCountReceipt,
    ErrorEnvelope,
)
from app.services.cv_count_service import CVCountService

router = APIRouter()
cv_count_service = CVCountService()


@router.post(
    "/count-records",
    response_model=CVCountBatchResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorEnvelope, "description": "Malformed JSON"},
        409: {"model": ErrorEnvelope, "description": "CV record conflict"},
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
