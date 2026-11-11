import pytest
from pydantic import ValidationError

from src.config import DEVELOPMENT_AUTH_SECRET, Settings


def test_settings_defaults_are_local_and_reproducible():
    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.app_name == "Task Manager API"
    assert settings.database_url == "sqlite:///./task_manager.db"
    assert settings.api_v1_prefix == "/api/v1"


@pytest.mark.parametrize(
    "values",
    [
        {"app_name": ""},
        {"database_url": ""},
        {"api_v1_prefix": "api/v1"},
        {"app_env": "staging"},
    ],
)
def test_settings_reject_invalid_values(values):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)


def test_production_rejects_the_development_secret():
    with pytest.raises(ValidationError, match="unique AUTH_SECRET_KEY"):
        Settings(
            _env_file=None,
            app_env="production",
            auth_secret_key=DEVELOPMENT_AUTH_SECRET,
        )


def test_production_accepts_a_custom_secret():
    settings = Settings(
        _env_file=None,
        app_env="production",
        auth_secret_key="a-unique-production-secret-with-more-than-32-characters",
    )
    assert settings.app_env == "production"


def test_settings_reject_blank_auth_secret():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, auth_secret_key=" " * 40)
