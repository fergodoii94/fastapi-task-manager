from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Task Manager API"
    version: str = "1.1.0"
    secret_key: str = os.getenv("SECRET_KEY", "development-secret-key-change-me")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    demo_username: str = os.getenv("DEMO_USERNAME", "admin")
    demo_password: str = os.getenv("DEMO_PASSWORD", "admin123")


settings = Settings()
