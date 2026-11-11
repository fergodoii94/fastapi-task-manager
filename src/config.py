from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEVELOPMENT_AUTH_SECRET = (
    "development-only-change-this-secret-before-deployment-please"
)


class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = Field(default="Task Manager API", min_length=1, max_length=120)
    database_url: str = Field(default="sqlite:///./task_manager.db", min_length=1)
    api_v1_prefix: str = Field(default="/api/v1", pattern=r"^/.*$")
    auth_secret_key: str = Field(default=DEVELOPMENT_AUTH_SECRET, min_length=32)
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if not self.auth_secret_key.strip():
            raise ValueError("AUTH_SECRET_KEY must not be blank")
        if (
            self.app_env == "production"
            and self.auth_secret_key == DEVELOPMENT_AUTH_SECRET
        ):
            raise ValueError(
                "A unique AUTH_SECRET_KEY is required when APP_ENV=production"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
