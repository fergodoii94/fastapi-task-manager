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
    assert client.get("/api/v1/tasks/" + str(task["id"])).json()["id"] == task["id"]

def test_list_tasks_filters_status(client):
    client.post("/api/v1/tasks", json={"title": "Pending"})
    client.post("/api/v1/tasks", json={"title": "Done", "status": "completed"})
    body = client.get("/api/v1/tasks?status=completed").json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "completed"

def test_update_task(client):
    task = client.post("/api/v1/tasks", json={"title": "Initial"}).json()
    response = client.patch("/api/v1/tasks/" + str(task["id"]), json={"title": "Updated", "status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_delete_task(client):
    task = client.post("/api/v1/tasks", json={"title": "Delete me"}).json()
    assert client.delete("/api/v1/tasks/" + str(task["id"])).status_code == 204
    assert client.get("/api/v1/tasks/" + str(task["id"])).status_code == 404

def test_invalid_priority_is_rejected(client):
    assert client.post("/api/v1/tasks", json={"title": "Bad", "priority": 9}).status_code == 422

def test_missing_task_returns_404(client):
    assert client.get("/api/v1/tasks/999").status_code == 404
