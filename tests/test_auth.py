from src.database import get_db
from src.main import app
from src.models import User
from src.security import create_access_token


def register(client, email, password="correct-horse-battery"):
    return client.post("/api/v1/auth/register", json={"email": email, "password": password})


def test_registration_normalizes_email_and_never_returns_password(client):
    response = register(client, "  SECOND@example.com ")
    assert response.status_code == 201
    assert response.json()["email"] == "second@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_duplicate_email_is_rejected(client):
    response = register(client, "owner@example.com")
    assert response.status_code == 409


def test_short_password_is_rejected(client):
    response = register(client, "short@example.com", "short")
    assert response.status_code == 422


def test_login_returns_bearer_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] > 0


def test_wrong_password_is_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "incorrect-password"},
    )
    assert response.status_code == 401


def test_me_returns_authenticated_user(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"


def test_tasks_require_authentication(client):
    client.headers.pop("Authorization")
    assert client.get("/api/v1/tasks").status_code == 401
    assert client.post("/api/v1/tasks", json={"title": "No token"}).status_code == 401


def test_invalid_bearer_token_is_rejected(client):
    client.headers["Authorization"] = "Bearer not-a-valid-token"
    assert client.get("/api/v1/auth/me").status_code == 401


def test_inactive_legacy_account_cannot_login_or_use_an_existing_token(client):
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        legacy_user = User(
            email="legacy-migration@example.com",
            password_hash="!account-disabled-by-migration!",
            is_active=False,
        )
        db.add(legacy_user)
        db.commit()
        legacy_user_id = legacy_user.id
    finally:
        db_generator.close()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "legacy-migration@example.com",
            "password": "any-password-at-all",
        },
    )
    assert login.status_code == 401

    token, _ = create_access_token(legacy_user_id)
    client.headers["Authorization"] = f"Bearer {token}"
    assert client.get("/api/v1/auth/me").status_code == 401
