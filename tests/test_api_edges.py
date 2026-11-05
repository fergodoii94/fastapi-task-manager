from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_update_missing_task_returns_404():
    response = client.patch("/api/v1/tasks/999999", json={"title": "Updated"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_missing_task_returns_404():
    response = client.delete("/api/v1/tasks/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_task_title_length_is_validated(client):
    response = client.post("/api/v1/tasks", json={"title": "x" * 161})
    assert response.status_code == 422


def test_task_list_empty_filter_and_pagination(client):
    response = client.get("/api/v1/tasks?page=1&page_size=10&status=archived")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []
