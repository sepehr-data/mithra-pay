# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.config import settings


# -----------------------------
# Password hashing
# -----------------------------
def hash_password(password: str) -> str:
    """
    Hash a plain text password using werkzeug's PBKDF2.
    """
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    """
    if not password_hash:
        return False
    return check_password_hash(password_hash, password)


# -----------------------------
# JWT helpers
# -----------------------------
def create_access_token(
    subject: str | int,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """
    Create a signed JWT token for a user.
    subject: usually user.id
    extra_claims: e.g. roles, phone_verified
    """
    if expires_minutes is None:
      expires_minutes = settings.JWT_EXPIRE_MINUTES

    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_minutes)

    payload = {
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
    """
    Decode and validate a JWT.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on invalid tokens.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    return payload
