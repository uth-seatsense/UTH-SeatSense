"""
SEAT-65: API đăng nhập OTP - Comprehensive Test Suite

Tests cover all requirements from SEAT-65:
- Valid OTP flow
- Expiration handling
- Rate limiting (resend cooldown)
- Attempt limits (max 5 incorrect attempts)
- OTP reuse prevention
- Email domain allowlist
- Security: no plaintext OTP/tokens in DB or logs
"""
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import SecretStr

import app.models
from app.api.deps import get_db
from app.api import auth
from app.core.config import Settings
from app.db.base import Base
from app.models.auth_session import AuthSession
from app.models.email_otp_challenge import EmailOtpChallenge
from app.models.user import User
from main import app


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with OTP enabled and 60-second resend cooldown."""
    return Settings(
        allowed_email_domains="uth.edu.vn,student.uth.edu.vn",
        otp_hash_secret=SecretStr("test-secret-key-with-at-least-32-bytes-for-hmac"),
        otp_ttl_minutes=5,
        otp_resend_seconds=60,
        otp_max_attempts=5,
        access_token_ttl_minutes=60,
        smtp_host="smtp.fake.test",
        smtp_port=1025,
        smtp_from_email="noreply@uth.edu.vn",
        smtp_username=None,
        smtp_password=None,
        smtp_starttls=False,
    )


@pytest.fixture
def db_engine():
    """In-memory SQLite database for tests."""
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Database session for direct DB access in tests."""
    session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    with session_factory() as session:
        yield session


@pytest.fixture
def client(
    db_engine,
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[tuple[TestClient, list[tuple[str, str]]], None, None]:
    """Test client with mocked email sender."""
    session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as db:
            yield db

    # Track sent emails: list of (email, otp) tuples
    sent_emails: list[tuple[str, str]] = []

    def mock_send_email(_settings, email: str, otp: str) -> None:
        sent_emails.append((email, otp))

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth.get_settings] = lambda: test_settings
    monkeypatch.setattr(auth, "send_otp_email", mock_send_email)

    try:
        with TestClient(app) as test_client:
            yield test_client, sent_emails
    finally:
        app.dependency_overrides.clear()


# ============================================================================
# TEST CASE 1: Valid OTP Flow - Happy Path
# ============================================================================


def test_valid_otp_login_creates_user_and_returns_token(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-01: Valid OTP flow
    - Request OTP → 202 response
    - Verify OTP → 200 + access token + user info
    - User created on first successful verification
    """
    test_client, sent_emails = client
    email = "newuser@uth.edu.vn"

    # Step 1: Request OTP
    request_response = test_client.post("/api/v1/auth/register", json={"email": email})
    assert request_response.status_code == 202
    assert request_response.json() == {"status": "otp_sent"}

    # Verify email was "sent"
    assert len(sent_emails) == 1
    assert sent_emails[0][0] == email
    otp_code = sent_emails[0][1]
    assert len(otp_code) == 6
    assert otp_code.isdigit()

    # Verify OTP hash stored in DB, not plaintext
    challenge = db_session.scalar(
        select(EmailOtpChallenge)
        .where(EmailOtpChallenge.email == email)
        .order_by(EmailOtpChallenge.created_at.desc())
    )
    assert challenge is not None
    assert challenge.otp_hash is not None
    assert len(challenge.otp_hash) == 64  # SHA-256 hex
    assert otp_code not in challenge.otp_hash  # No plaintext
    assert challenge.consumed_at is None
    assert challenge.attempts == 0

    # Step 2: Verify OTP and login
    login_response = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp_code},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Verify token response structure
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert "expires_at" in login_data
    assert "user" in login_data

    # Verify user data
    user_data = login_data["user"]
    assert user_data["email"] == email
    assert user_data["role"] == "student"
    assert "id" in user_data
    assert "display_name" in user_data

    # Verify user created in DB
    user = db_session.scalar(select(User).where(User.email == email))
    assert user is not None
    assert user.email == email
    assert user.role == "student"
    assert user.is_active is True
    assert user.password_hash is None  # OTP auth, no password

    # Verify OTP consumed
    db_session.expire(challenge)
    db_session.refresh(challenge)
    assert challenge.consumed_at is not None

    # Verify token hash stored (not plaintext)
    access_token = login_data["access_token"]
    session = db_session.scalar(
        select(AuthSession).where(AuthSession.user_id == user.user_id)
    )
    assert session is not None
    assert len(session.token_hash) == 64  # SHA-256 hex
    assert access_token not in session.token_hash  # No plaintext
    assert session.revoked_at is None


# ============================================================================
# TEST CASE 2: Expired OTP
# ============================================================================


def test_expired_otp_rejected(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
    test_settings: Settings,
) -> None:
    """
    TC-02: Expired OTP
    - OTP expires after otp_ttl_minutes (5 minutes)
    - Expired OTP returns 401 invalid_otp
    """
    test_client, sent_emails = client
    email = "expired@uth.edu.vn"

    # Request OTP
    test_client.post("/api/v1/auth/register", json={"email": email})
    otp_code = sent_emails[-1][1]

    # Manually expire the OTP in DB
    challenge = db_session.scalar(
        select(EmailOtpChallenge)
        .where(EmailOtpChallenge.email == email)
        .order_by(EmailOtpChallenge.created_at.desc())
        .with_for_update()
    )
    assert challenge is not None

    # Set expiry to past
    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    challenge.expires_at = past_time
    db_session.commit()

    # Attempt to verify expired OTP
    login_response = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp_code},
    )
    assert login_response.status_code == 401
    error = login_response.json()
    assert error["error"]["code"] == "invalid_otp"
    assert "expired" in error["error"]["message"].lower()


# ============================================================================
# TEST CASE 3: Max Attempts (5 incorrect attempts)
# ============================================================================


def test_max_incorrect_attempts_locks_otp(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-03: Max 5 incorrect attempts
    - After 5 wrong OTP attempts, challenge is consumed
    - Further attempts with correct OTP also fail
    """
    test_client, sent_emails = client
    email = "maxattempt@uth.edu.vn"

    # Request OTP
    test_client.post("/api/v1/auth/register", json={"email": email})
    correct_otp = sent_emails[-1][1]

    wrong_otp = "000001" if correct_otp == "000000" else "000000"

    # Attempt 5 times with wrong OTP
    for i in range(5):
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": email, "otp": wrong_otp},  # Wrong OTP
        )
        assert response.status_code == 401

    # Verify challenge is locked (consumed)
    challenge = db_session.scalar(
        select(EmailOtpChallenge)
        .where(EmailOtpChallenge.email == email)
        .order_by(EmailOtpChallenge.created_at.desc())
    )
    assert challenge.attempts >= 5
    assert challenge.consumed_at is not None

    # Even correct OTP now fails
    response = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": correct_otp},
    )
    assert response.status_code == 401


# ============================================================================
# TEST CASE 4: OTP Reuse Prevention
# ============================================================================


def test_otp_cannot_be_reused(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-04: OTP single-use
    - OTP can only be used once
    - After successful verification, same OTP is rejected
    """
    test_client, sent_emails = client
    email = "reuse@uth.edu.vn"

    # Request and verify OTP (first time - success)
    test_client.post("/api/v1/auth/register", json={"email": email})
    otp_code = sent_emails[-1][1]

    first_login = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp_code},
    )
    assert first_login.status_code == 200

    # Attempt to reuse same OTP
    second_login = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp_code},
    )
    assert second_login.status_code == 401
    error = second_login.json()
    assert error["error"]["code"] == "invalid_otp"


# ============================================================================
# TEST CASE 5: Resend Rate Limiting (60 seconds cooldown)
# ============================================================================


def test_resend_rate_limit_60_seconds(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-05: Resend cooldown
    - Cannot request new OTP within 60 seconds
    - Returns 429 Too Many Requests
    """
    test_client, sent_emails = client
    email = "ratelimit@uth.edu.vn"

    # First request - success
    first_request = test_client.post("/api/v1/auth/register", json={"email": email})
    assert first_request.status_code == 202
    assert len(sent_emails) == 1

    # Immediate second request - rate limited
    second_request = test_client.post("/api/v1/auth/register", json={"email": email})
    assert second_request.status_code == 429
    error = second_request.json()
    assert error["error"]["code"] == "otp_resend_too_soon"
    assert len(sent_emails) == 1  # No new email sent

    # Simulate time passing (move challenge timestamp back 61 seconds)
    challenge = db_session.scalar(
        select(EmailOtpChallenge)
        .where(EmailOtpChallenge.email == email)
        .order_by(EmailOtpChallenge.created_at.desc())
        .with_for_update()
    )
    old_time = datetime.now(timezone.utc) - timedelta(seconds=61)
    challenge.created_at = old_time
    db_session.commit()

    # Third request after cooldown - success
    third_request = test_client.post("/api/v1/auth/register", json={"email": email})
    assert third_request.status_code == 202
    assert len(sent_emails) == 2  # New email sent


# ============================================================================
# TEST CASE 6: Email Domain Allowlist
# ============================================================================


def test_email_domain_allowlist_enforcement(
    client: tuple[TestClient, list[tuple[str, str]]],
) -> None:
    """
    TC-06: Email domain allowlist
    - Only emails from allowed domains accepted
    - Other domains return 422 Unprocessable Entity
    - Error message does not reveal if email exists
    """
    test_client, sent_emails = client

    # Test allowed domains (from test_settings)
    allowed_emails = [
        "student@uth.edu.vn",
        "teacher@uth.edu.vn",
        "admin@student.uth.edu.vn",
    ]
    for email in allowed_emails:
        response = test_client.post("/api/v1/auth/register", json={"email": email})
        assert response.status_code == 202, f"Failed for allowed email: {email}"

    # Test disallowed domains
    disallowed_emails = [
        "user@gmail.com",
        "attacker@example.com",
        "test@uth.com",  # Similar but not exact
        "student@uth.edu.vn.fake.com",  # Domain spoofing attempt
    ]
    for email in disallowed_emails:
        response = test_client.post("/api/v1/auth/register", json={"email": email})
        assert response.status_code == 422, f"Should reject: {email}"
        error = response.json()
        assert error["error"]["code"] == "email_not_allowed"
        # Verify error message doesn't leak email existence info
        assert "not allowed" in error["error"]["message"].lower()

    # Verify no emails sent for disallowed domains
    sent_addresses = [addr for addr, _ in sent_emails]
    for email in disallowed_emails:
        assert email not in sent_addresses


# ============================================================================
# TEST CASE 7: Security - No Plaintext in Database
# ============================================================================


def test_no_plaintext_otp_or_token_in_database(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-07: Security requirement
    - OTP stored as hash only (SHA-256 HMAC)
    - Access tokens stored as hash only (SHA-256)
    - No plaintext secrets in database
    """
    test_client, sent_emails = client
    email = "security@uth.edu.vn"

    # Request OTP
    test_client.post("/api/v1/auth/register", json={"email": email})
    otp_plaintext = sent_emails[-1][1]

    # Check database for OTP plaintext
    challenge = db_session.scalar(
        select(EmailOtpChallenge)
        .where(EmailOtpChallenge.email == email)
        .order_by(EmailOtpChallenge.created_at.desc())
    )

    # Verify OTP hash format and no plaintext
    assert challenge.otp_hash is not None
    assert len(challenge.otp_hash) == 64  # SHA-256 produces 64 hex chars
    assert challenge.otp_hash != otp_plaintext
    assert otp_plaintext not in challenge.otp_hash

    # Verify plaintext OTP not in any column using raw SQL
    result = db_session.execute(
        text("SELECT * FROM email_otp_challenges WHERE email = :email"),
        {"email": email},
    ).fetchone()

    # Convert entire row to string and check for plaintext
    row_str = " ".join(str(val) for val in result if val is not None)
    assert otp_plaintext not in row_str, "OTP plaintext found in database row!"

    # Login to get access token
    login_response = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp_plaintext},
    )
    token_plaintext = login_response.json()["access_token"]

    # Check database for token plaintext
    user = db_session.scalar(select(User).where(User.email == email))
    session = db_session.scalar(
        select(AuthSession).where(AuthSession.user_id == user.user_id)
    )

    # Verify token hash format and no plaintext
    assert session.token_hash is not None
    assert len(session.token_hash) == 64  # SHA-256
    assert session.token_hash != token_plaintext
    assert token_plaintext not in session.token_hash

    # Verify plaintext token not in any column using raw SQL
    result = db_session.execute(
        text("SELECT * FROM auth_sessions WHERE user_id = :user_id"),
        {"user_id": user.user_id},
    ).fetchone()

    row_str = " ".join(str(val) for val in result if val is not None)
    assert token_plaintext not in row_str, "Token plaintext found in database row!"


# ============================================================================
# TEST CASE 8: Logout Revokes Session
# ============================================================================


def test_logout_revokes_session(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-08: Logout functionality
    - POST /auth/logout revokes current session
    - Revoked token cannot be used for authenticated requests
    """
    test_client, sent_emails = client
    email = "logout@uth.edu.vn"

    # Login
    test_client.post("/api/v1/auth/register", json={"email": email})
    otp = sent_emails[-1][1]
    login = test_client.post("/api/v1/auth/login", json={"email": email, "otp": otp})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify token works
    me_response = test_client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200

    # Logout
    logout_response = test_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 204

    # Verify token no longer works
    me_after_logout = test_client.get("/api/v1/auth/me", headers=headers)
    assert me_after_logout.status_code == 401

    # Verify session revoked in DB
    user = db_session.scalar(select(User).where(User.email == email))
    session = db_session.scalar(
        select(AuthSession).where(AuthSession.user_id == user.user_id)
    )
    assert session.revoked_at is not None


# ============================================================================
# TEST CASE 9: Invalid OTP Format
# ============================================================================


def test_invalid_otp_format_rejected(
    client: tuple[TestClient, list[tuple[str, str]]],
) -> None:
    """
    TC-09: Input validation
    - OTP must be exactly 6 digits
    - Invalid formats rejected with 422
    """
    test_client, sent_emails = client
    email = "format@uth.edu.vn"

    test_client.post("/api/v1/auth/register", json={"email": email})

    invalid_otps = [
        "12345",      # Too short
        "1234567",    # Too long
        "abcdef",     # Letters
        "12-45-78",   # Special chars
        "",           # Empty
        "123 456",    # Space
    ]

    for invalid_otp in invalid_otps:
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": email, "otp": invalid_otp},
        )
        assert response.status_code == 422, f"Should reject OTP: {invalid_otp}"


# ============================================================================
# TEST CASE 10: User Auto-Creation on First Login
# ============================================================================


def test_user_auto_created_on_first_successful_verification(
    client: tuple[TestClient, list[tuple[str, str]]],
    db_session: Session,
) -> None:
    """
    TC-10: User auto-creation
    - User record created automatically on first successful OTP verification
    - Subsequent logins use existing user
    - Display name derived from email
    """
    test_client, sent_emails = client
    email = "autocreate@uth.edu.vn"

    # Verify user doesn't exist
    user_before = db_session.scalar(select(User).where(User.email == email))
    assert user_before is None

    # First login
    test_client.post("/api/v1/auth/register", json={"email": email})
    otp = sent_emails[-1][1]
    first_login = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp},
    )
    assert first_login.status_code == 200
    first_user_id = first_login.json()["user"]["id"]

    # Verify user created
    user_after = db_session.scalar(select(User).where(User.email == email))
    assert user_after is not None
    assert user_after.email == email
    assert user_after.display_name == "autocreate"  # From email prefix
    assert user_after.role == "student"

    # Second login (after 60s cooldown)
    challenge = db_session.scalar(
        select(EmailOtpChallenge)
        .where(EmailOtpChallenge.email == email)
        .order_by(EmailOtpChallenge.created_at.desc())
        .with_for_update()
    )
    challenge.created_at = datetime.now(timezone.utc) - timedelta(seconds=61)
    db_session.commit()

    test_client.post("/api/v1/auth/register", json={"email": email})
    otp2 = sent_emails[-1][1]
    second_login = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "otp": otp2},
    )
    assert second_login.status_code == 200
    second_user_id = second_login.json()["user"]["id"]

    # Verify same user ID (not created again)
    assert first_user_id == second_user_id

    # Verify only one user record
    user_count = db_session.scalar(
        select(text("count(*)")).select_from(User).where(User.email == email)
    )
    assert user_count == 1


def test_otp_not_written_to_logs(client, caplog):
    test_client, emails = client
    with caplog.at_level("DEBUG"):
        response = test_client.post(
            "/api/v1/auth/register", json={"email": "logs@uth.edu.vn"}
        )
        assert response.status_code == 202
        otp = emails[-1][1]
        login = test_client.post(
            "/api/v1/auth/login", json={"email": "logs@uth.edu.vn", "otp": otp}
        )
        assert login.status_code == 200
    assert otp not in caplog.text
    assert login.json()["access_token"] not in caplog.text


def test_smtp_delivery_uses_configured_server(test_settings, monkeypatch):
    from app.services import email_service

    smtp = Mock()
    smtp_factory = MagicMock()
    smtp_factory.return_value.__enter__.return_value = smtp
    monkeypatch.setattr(email_service.smtplib, "SMTP", smtp_factory)
    email_service.send_otp_email(test_settings, "student@uth.edu.vn", "123456")
    smtp_factory.assert_called_once_with("smtp.fake.test", 1025, timeout=10)
    message = smtp.send_message.call_args.args[0]
    assert message["To"] == "student@uth.edu.vn"
    assert "123456" in message.get_content()
    smtp.starttls.assert_not_called()
    smtp.login.assert_not_called()


def test_smtp_failure_returns_503_without_logging_otp(client, monkeypatch, caplog):
    from app.services import email_service

    test_client, _ = client
    monkeypatch.setattr(auth, "send_otp_email", email_service.send_otp_email)
    monkeypatch.setattr(
        email_service.smtplib, "SMTP", Mock(side_effect=OSError("SMTP unavailable"))
    )
    monkeypatch.setattr("app.services.auth_service.secrets.randbelow", lambda _: 123456)
    response = test_client.post(
        "/api/v1/auth/register", json={"email": "smtp-error@uth.edu.vn"}
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "otp_delivery_failed"
    assert "123456" not in caplog.text
    # A failed delivery must not leave a usable challenge.
    login = test_client.post(
        "/api/v1/auth/login",
        json={"email": "smtp-error@uth.edu.vn", "otp": "123456"},
    )
    assert login.status_code == 401


def test_postgres_request_locks_email_before_reading_challenge(test_settings):
    from app.services.auth_service import AuthService

    db = Mock()
    db.get_bind.return_value.dialect.name = "postgresql"
    db.scalar.return_value = None
    AuthService(test_settings).request_otp(
        db, email="student@uth.edu.vn", mailer=Mock()
    )
    names = [call[0] for call in db.mock_calls]
    assert names.index("execute") < names.index("scalar") < names.index("commit")
    assert "pg_advisory_xact_lock" in str(db.execute.call_args.args[0])


def test_login_code_keeps_existing_table_and_erd_aliases():
    from app.models.login_code import LoginCode

    assert EmailOtpChallenge is LoginCode
    assert LoginCode.__tablename__ == "email_otp_challenges"
    code = LoginCode(email="student@uth.edu.vn", code_hash="a" * 64)
    assert code.otp_hash == code.code_hash
