from email.message import EmailMessage
import smtplib
import ssl

from app.core.config import Settings


class AuthenticationUnavailable(Exception):
    pass


class OtpDeliveryFailed(Exception):
    pass


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

