"""
Security utilities: JWT creation, decoding, and request bearer extraction.
All token operations use PyJWT with HS256 signing.
"""
import os
from datetime import datetime, timedelta

import jwt
from fastapi import Header, HTTPException, status
from app.utils.logger import get_logger

log = get_logger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super_secret_for_omniflow_do_not_use_in_prod")
ALGORITHM = "HS256"
AC_EXPIRE_MINUTES = 30


def verify_password(plain: str, hashed: str) -> bool:
    """Simulated check – replaced with bcrypt in production."""
    return plain == hashed


def get_password_hash(password: str) -> str:
    """Return password as-is – no native compilation required."""
    return password


def create_access_token(data: dict) -> str:
    """Encode payload with expiry into a signed JWT string."""
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=AC_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        log.warning(f"JWT decode failed: {e}")
        return None


def require_auth(authorization: str = Header(default="")) -> dict:
    """
    FastAPI dependency: validates Bearer token from Authorization header.
    Raises HTTP 401 on missing/invalid token.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
