import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
import src.models  # noqa: F401


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        registration = test_client.post(
            "/api/v1/auth/register",
            json={"email": "owner@example.com", "password": "correct-horse-battery"},
        )
        assert registration.status_code == 201
        login = test_client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "correct-horse-battery"},
        )
        assert login.status_code == 200
        test_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
