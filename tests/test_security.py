import jwt
import pytest

from src.config import get_settings
from src.security import decode_access_token


def test_access_token_requires_expiration_issued_at_and_subject_claims():
    token = jwt.encode(
        {"sub": "1"},
        get_settings().auth_secret_key,
        algorithm="HS256",
    )

    with pytest.raises(jwt.MissingRequiredClaimError):
        decode_access_token(token)
