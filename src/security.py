from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from src.config import get_settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.access_token_expire_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, settings.auth_secret_key, algorithm=ALGORITHM)
    return token, expires_in


def decode_access_token(token: str) -> int:
    settings = get_settings()
    payload = jwt.decode(token, settings.auth_secret_key, algorithms=[ALGORITHM])
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.isdigit():
        raise jwt.InvalidTokenError("Invalid token subject")
    return int(subject)
