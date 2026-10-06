from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from src.config import settings

logger = logging.getLogger("task_manager.auth")
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class TokenPayload(BaseModel):
    sub: str
    exp: int


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")


def _b64decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def create_access_token(subject: str) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + (settings.access_token_expire_minutes * 60),
    }
    header = {"alg": settings.algorithm, "typ": "JWT"}
    encoded_header = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}"


def verify_token(token: str) -> TokenPayload:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_signature = hmac.new(settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        calculated_signature = _b64decode(signature_b64)

        if not hmac.compare_digest(expected_signature, calculated_signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature is invalid")

        payload = json.loads(_b64decode(payload_b64).decode("utf-8"))
        exp = int(payload.get("exp", 0))
        if exp < int(time.time()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        return TokenPayload(sub=payload["sub"], exp=exp)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.warning("Token verification failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid") from exc


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    return {"sub": payload.sub}


__all__ = ["LoginRequest", "create_access_token", "get_current_user", "verify_token"]
