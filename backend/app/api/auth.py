import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_current_user
from app.api.errors import api_error
from app.core.config import Settings, settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthUser,
    OtpLoginRequest,
    OtpRequest,
    OtpRequestResponse,
    TokenResponse,
)
from app.services.auth_service import (
    AuthService,
    AuthenticationUnavailable,
    EmailNotAllowed,
    InvalidOtp,
    OtpDeliveryFailed,
    OtpRateLimited,
)
from app.services.email_service import send_otp_email

logger = logging.getLogger(__name__)
router = APIRouter()


def get_settings() -> Settings:
    return settings


@router.post(
    "/register",
    response_model=OtpRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_login_otp(
    payload: OtpRequest,
    db: Session = Depends(get_db),
    config: Settings = Depends(get_settings),
) -> OtpRequestResponse:
    try:
        AuthService(config).request_otp(
            db,
            email=str(payload.email),
            mailer=send_otp_email,
        )
    except EmailNotAllowed:
        raise api_error(422, "email_not_allowed", "This email address is not allowed") from None
    except OtpRateLimited:
        raise api_error(429, "otp_resend_too_soon", "Wait before requesting another code") from None
    except AuthenticationUnavailable:
        raise api_error(
            503,
            "email_auth_unavailable",
            "Email OTP authentication is not configured",
        ) from None
    except OtpDeliveryFailed:
        logger.exception("Failed to deliver an email OTP")
        raise api_error(503, "otp_delivery_failed", "The verification email could not be sent") from None
    return OtpRequestResponse()


@router.post("/login", response_model=TokenResponse)
def verify_login_otp(
    payload: OtpLoginRequest,
    db: Session = Depends(get_db),
    config: Settings = Depends(get_settings),
) -> TokenResponse:
    try:
        token, expires_at, user = AuthService(config).verify_otp(
            db, email=str(payload.email), otp=payload.otp
        )
    except AuthenticationUnavailable:
        raise api_error(
            503,
            "email_auth_unavailable",
            "Email OTP authentication is not configured",
        ) from None
    except InvalidOtp:
        raise api_error(401, "invalid_otp", "The verification code is invalid or expired") from None
    return TokenResponse(
        access_token=token,
        expires_at=expires_at,
        user=AuthUser(
            id=user.user_id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
        ),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Session = Depends(get_db),
) -> Response:
    context.session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=AuthUser)
def get_me(user: User = Depends(get_current_user)) -> AuthUser:
    return AuthUser(
        id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
    )
