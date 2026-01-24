from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt

from core.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: UUID) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
