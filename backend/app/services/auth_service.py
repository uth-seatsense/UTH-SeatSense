from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import hashlib
import hmac
import secrets
import smtplib
import ssl

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.auth_session import AuthSession
from app.models.email_otp_challenge import EmailOtpChallenge
from app.models.user import User


class AuthenticationUnavailable(Exception):
    pass


class EmailNotAllowed(Exception):
    pass


class OtpRateLimited(Exception):
    pass


class InvalidOtp(Exception):
    pass


class OtpDeliveryFailed(Exception):
    pass


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _otp_digest(settings: Settings, email: str, otp: str) -> str:
    if settings.otp_hash_secret is None or not settings.otp_hash_secret.get_secret_value():
        raise AuthenticationUnavailable
    message = f"{email}:{otp}".encode("utf-8")
    return hmac.new(
        settings.otp_hash_secret.get_secret_value().encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def _configuration_ready(settings: Settings) -> bool:
    return bool(
        settings.email_domain_allowlist()
        and settings.otp_hash_secret
        and len(settings.otp_hash_secret.get_secret_value()) >= 32
        and settings.smtp_host
        and settings.smtp_from_email
        and bool(settings.smtp_username)
        == bool(settings.smtp_password and settings.smtp_password.get_secret_value())
    )


def send_otp_email(settings: Settings, email: str, otp: str) -> None:
    if not _configuration_ready(settings):
        raise AuthenticationUnavailable

    message = EmailMessage()
    message["Subject"] = "Mã xác minh UTH-SeatSense"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(
        f"Mã xác minh của bạn là {otp}. Mã có hiệu lực trong "
        f"{settings.otp_ttl_minutes} phút và chỉ sử dụng được một lần."
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_starttls:
                smtp.starttls(context=ssl.create_default_context())
            if settings.smtp_username:
                if settings.smtp_password is None:
                    raise AuthenticationUnavailable
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password.get_secret_value(),
                )
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise OtpDeliveryFailed from exc


class AuthService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def request_otp(
        self,
        db: Session,
        *,
        email: str,
        mailer=send_otp_email,
        now: datetime | None = None,
    ) -> None:
        normalized_email = email.strip().lower()
        if not _configuration_ready(self.settings):
            raise AuthenticationUnavailable
        domain = normalized_email.rpartition("@")[2]
        if domain not in self.settings.email_domain_allowlist():
            raise EmailNotAllowed

        current_time = now or datetime.now(timezone.utc)
        latest = db.scalar(
            select(EmailOtpChallenge)
            .where(EmailOtpChallenge.email == normalized_email)
            .order_by(EmailOtpChallenge.created_at.desc())
            .limit(1)
        )
        if latest and (
            current_time - _utc(latest.created_at)
        ).total_seconds() < self.settings.otp_resend_seconds:
            raise OtpRateLimited

        otp = f"{secrets.randbelow(1_000_000):06d}"
        challenge = EmailOtpChallenge(
            email=normalized_email,
            otp_hash=_otp_digest(self.settings, normalized_email, otp),
            created_at=current_time,
            expires_at=current_time + timedelta(minutes=self.settings.otp_ttl_minutes),
        )
        db.add(challenge)
        db.commit()

        try:
            mailer(self.settings, normalized_email, otp)
        except (AuthenticationUnavailable, OtpDeliveryFailed):
            challenge.consumed_at = current_time
            db.commit()
            raise

    def verify_otp(
        self,
        db: Session,
        *,
        email: str,
        otp: str,
        now: datetime | None = None,
    ) -> tuple[str, datetime, User]:
        normalized_email = email.strip().lower()
        if not _configuration_ready(self.settings):
            raise AuthenticationUnavailable
        if normalized_email.rpartition("@")[2] not in self.settings.email_domain_allowlist():
            raise InvalidOtp

        current_time = now or datetime.now(timezone.utc)
        challenge = db.scalar(
            select(EmailOtpChallenge)
            .where(EmailOtpChallenge.email == normalized_email)
            .order_by(EmailOtpChallenge.created_at.desc())
            .limit(1)
            .with_for_update()
        )
        if (
            challenge is None
            or challenge.consumed_at is not None
            or _utc(challenge.expires_at) <= current_time
            or challenge.attempts >= self.settings.otp_max_attempts
        ):
            raise InvalidOtp

        expected_hash = _otp_digest(self.settings, normalized_email, otp)
        if not hmac.compare_digest(challenge.otp_hash, expected_hash):
            challenge.attempts += 1
            if challenge.attempts >= self.settings.otp_max_attempts:
                challenge.consumed_at = current_time
            db.commit()
            raise InvalidOtp

        challenge.consumed_at = current_time
        user = db.scalar(
            select(User).where(func.lower(User.email) == normalized_email)
        )
        if user is None:
            user = User(
                email=normalized_email,
                display_name=normalized_email.partition("@")[0][:100],
                password_hash=None,
                role="student",
                is_active=True,
            )
            db.add(user)
            db.flush()

        access_token = secrets.token_urlsafe(32)
        expires_at = current_time + timedelta(
            minutes=self.settings.access_token_ttl_minutes
        )
        db.add(
            AuthSession(
                user_id=user.user_id,
                token_hash=hashlib.sha256(access_token.encode("utf-8")).hexdigest(),
                created_at=current_time,
                expires_at=expires_at,
            )
        )
        db.commit()
        return access_token, expires_at, user
