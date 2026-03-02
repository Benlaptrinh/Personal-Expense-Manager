from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayloadError(Exception):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(subject: str, token_type: str, role: str | None, expires_delta: timedelta) -> tuple[str, str, datetime]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    jti = str(uuid4())
    payload = {
        "sub": subject,
        "type": token_type,
        "role": role,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token, jti, expires_at


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as exc:
        raise TokenPayloadError("Invalid token") from exc

    if "sub" not in payload or "type" not in payload or "jti" not in payload:
        raise TokenPayloadError("Malformed token")

    return payload
