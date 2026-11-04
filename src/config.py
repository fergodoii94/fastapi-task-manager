from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Task Manager API", min_length=1, max_length=120)
    database_url: str = Field(default="sqlite:///./task_manager.db", min_length=1)
    api_v1_prefix: str = Field(default="/api/v1", pattern=r"^/.*$")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
