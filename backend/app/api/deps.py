from dataclasses import dataclass
from datetime import datetime, timezone
from collections.abc import Callable
import hashlib

from fastapi import Depends
from fastapi import Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import api_error
from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.models.user import User
from app.core.config import settings


def require_cv_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    configured = settings.cv_ingest_api_key.get_secret_value() if settings.cv_ingest_api_key else None
    if not configured or x_api_key is None or not hashlib.sha256(x_api_key.encode()).digest() == hashlib.sha256(configured.encode()).digest():
        raise api_error(401, "unauthorized", "A valid CV API key is required")

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: AuthSession


def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise api_error(401, "unauthorized", "A valid bearer token is required")

    token_hash = hashlib.sha256(credentials.credentials.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    auth_session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == token_hash,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
        )
    )
    if auth_session is None:
        raise api_error(401, "unauthorized", "The bearer token is invalid or expired")

    user = db.get(User, auth_session.user_id)
    if user is None or not user.is_active:
        raise api_error(403, "account_inactive", "The account is not active")
    return AuthContext(user=user, session=auth_session)


def get_current_user(context: AuthContext = Depends(get_auth_context)) -> User:
    return context.user


def require_roles(*roles: str) -> Callable[..., User]:
    allowed_roles = frozenset(roles)
    if not allowed_roles:
        raise ValueError("At least one allowed role is required")

    def check_role(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise api_error(403, "forbidden", "This role cannot access this endpoint")
        return user

    return check_role


__all__ = ["get_db", "get_auth_context", "get_current_user", "require_roles"]
