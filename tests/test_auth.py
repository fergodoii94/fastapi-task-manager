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
