# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, AppError


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    return check_password_hash(password_hash, password)


def create_access_token(
    subject: str | int,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    if expires_minutes is None:
        expires_minutes = settings.JWT_EXPIRE_MINUTES

    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_minutes)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )


def require_roles(claims: dict, allowed: List[str]):
    """
    Check that token claims contain at least one of allowed roles.
    Raise UnauthorizedError if not.
    """
    token_roles = claims.get("roles", [])
    if not token_roles:
        raise UnauthorizedError("no roles in token")

    if not any(r in token_roles for r in allowed):
        raise UnauthorizedError("insufficient role")
