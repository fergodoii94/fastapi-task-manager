import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_defaults_are_local_and_reproducible():
    settings = Settings(_env_file=None)

    assert settings.app_name == "Task Manager API"
    assert settings.database_url == "sqlite:///./task_manager.db"
    assert settings.api_v1_prefix == "/api/v1"


@pytest.mark.parametrize(
    "values",
    [
        {"app_name": ""},
        {"database_url": ""},
        {"api_v1_prefix": "api/v1"},
    ],
)
def test_settings_reject_invalid_values(values):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)
