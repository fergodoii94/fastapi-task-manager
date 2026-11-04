def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_task(client):
    response = client.post("/api/v1/tasks", json={"title": "Ship API", "priority": 4})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Ship API"
    assert task["priority"] == 4
    assert client.get(f"/api/v1/tasks/{task['id']}").json()["id"] == task["id"]


def test_create_task_trims_title(client):
    response = client.post("/api/v1/tasks", json={"title": "  Ship API  "})
    assert response.status_code == 201
    assert response.json()["title"] == "Ship API"


def test_create_task_rejects_whitespace_title(client):
    response = client.post("/api/v1/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_list_tasks_filters_status(client):
    client.post("/api/v1/tasks", json={"title": "Pending"})
    client.post("/api/v1/tasks", json={"title": "Done", "status": "completed"})
    body = client.get("/api/v1/tasks?status=completed").json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "completed"


def test_list_tasks_paginates_with_stable_order(client):
    for title in ("First", "Second", "Third"):
        response = client.post("/api/v1/tasks", json={"title": title})
        assert response.status_code == 201

    first_page = client.get("/api/v1/tasks?page=1&page_size=2").json()
    second_page = client.get("/api/v1/tasks?page=2&page_size=2").json()

    assert first_page["total"] == 3
    assert [item["title"] for item in first_page["items"]] == ["Third", "Second"]
    assert [item["title"] for item in second_page["items"]] == ["First"]


def test_list_tasks_rejects_invalid_pagination(client):
    assert client.get("/api/v1/tasks?page=0").status_code == 422
    assert client.get("/api/v1/tasks?page_size=101").status_code == 422


def test_update_task(client):
    task = client.post("/api/v1/tasks", json={"title": "Initial"}).json()
    response = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"title": "Updated", "status": "in_progress"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_update_task_can_clear_description(client):
    task = client.post(
        "/api/v1/tasks",
        json={"title": "Initial", "description": "Details"},
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"description": None},
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_task_rejects_empty_patch(client):
    task = client.post("/api/v1/tasks", json={"title": "Initial"}).json()
    response = client.patch(f"/api/v1/tasks/{task['id']}", json={})
    assert response.status_code == 422


def test_update_task_rejects_null_required_fields(client):
    task = client.post("/api/v1/tasks", json={"title": "Initial"}).json()
    for field in ("title", "status", "priority"):
        response = client.patch(f"/api/v1/tasks/{task['id']}", json={field: None})
        assert response.status_code == 422


def test_update_task_rejects_whitespace_title(client):
    task = client.post("/api/v1/tasks", json={"title": "Initial"}).json()
    response = client.patch(f"/api/v1/tasks/{task['id']}", json={"title": "   "})
    assert response.status_code == 422


def test_delete_task(client):
    task = client.post("/api/v1/tasks", json={"title": "Delete me"}).json()
    assert client.delete(f"/api/v1/tasks/{task['id']}").status_code == 204
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404


def test_invalid_priority_is_rejected(client):
    assert client.post(
        "/api/v1/tasks", json={"title": "Bad", "priority": 9}
    ).status_code == 422


def test_missing_task_returns_404(client):
    assert client.get("/api/v1/tasks/999").status_code == 404
