from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from src.core.config import get_settings

# Configure Passlib for bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def create_access_token(subject: str | int, expires_minutes: int = 60) -> str:
    """Create a signed JWT for the given subject with configurable expiry (default 60 minutes).
    The JWT is signed using HS256 and the secret from environment variable JWT_SECRET.
    """
    settings = get_settings()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {"sub": str(subject), "exp": expire}
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return token


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns payload dict if valid, otherwise None."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
