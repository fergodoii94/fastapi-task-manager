def create_user_and_token(client, email):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "another-correct-password"},
    )
    assert response.status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "another-correct-password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_users_only_see_their_own_tasks(client):
    own = client.post("/api/v1/tasks", json={"title": "Private task"}).json()
    other_token = create_user_and_token(client, "other@example.com")

    client.headers["Authorization"] = f"Bearer {other_token}"
    listing = client.get("/api/v1/tasks")
    assert listing.status_code == 200
    assert listing.json()["total"] == 0
    assert listing.json()["items"] == []
    assert client.get(f"/api/v1/tasks/{own['id']}").status_code == 404


def test_users_cannot_update_or_delete_another_users_task(client):
    own = client.post("/api/v1/tasks", json={"title": "Do not touch"}).json()
    other_token = create_user_and_token(client, "second@example.com")
    client.headers["Authorization"] = f"Bearer {other_token}"

    assert client.patch(
        f"/api/v1/tasks/{own['id']}", json={"title": "Hijacked"}
    ).status_code == 404
    assert client.delete(f"/api/v1/tasks/{own['id']}").status_code == 404

    # The owner still sees the original record unchanged.
    owner_login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "correct-horse-battery"},
    )
    client.headers["Authorization"] = f"Bearer {owner_login.json()['access_token']}"
    assert client.get(f"/api/v1/tasks/{own['id']}").json()["title"] == "Do not touch"
