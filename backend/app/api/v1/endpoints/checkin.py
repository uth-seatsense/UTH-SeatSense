from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import api_error
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.checkin import CheckInCreate, CheckInRead
from app.services.booking_service import BookingError
from app.services.checkin_service import CheckInService

router = APIRouter()


def _raise_checkin_error(error: BookingError) -> None:
    raise api_error(error.status_code, error.code, error.message) from None


@router.post("", response_model=CheckInRead)
def check_in(
    payload: CheckInCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckInRead:
    try:
        checked_in_at = CheckInService(settings).check_in(
            db,
            user_id=user.user_id,
            booking_id=payload.booking_id,
            qr_token=payload.qr_token,
        )
    except BookingError as error:
        _raise_checkin_error(error)
    return CheckInRead(
        booking_id=payload.booking_id,
        status="checked_in",
        checked_in_at=checked_in_at,
    )
