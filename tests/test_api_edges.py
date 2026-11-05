def test_task_title_length_is_validated(client):
    response = client.post("/api/v1/tasks", json={"title": "x" * 161})
    assert response.status_code == 422


def test_task_list_empty_filter_and_pagination(client):
    response = client.get("/api/v1/tasks?page=1&page_size=10&status=archived")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["items"] == []
