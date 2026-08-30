from unittest.mock import patch
from app.schemas.task import TaskCreate

import pytest


@pytest.fixture()
def project_id(client, auth_headers):
    response = client.post(
        "/projects/", json={"title": "Task Test Project"}, headers=auth_headers
    )
    return response.json()["id"]


def test_create_task(client, auth_headers, project_id):
    response = client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "My first task", "description": "Do something"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My first task"
    assert data["is_done"] is False
    assert data["project_id"] == project_id


def test_list_tasks_for_project(client, auth_headers, project_id):
    client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "Task 1"},
        headers=auth_headers,
    )
    client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "Task 2"},
        headers=auth_headers,
    )

    response = client.get(f"/projects/{project_id}/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_task(client, auth_headers, project_id):
    create_response = client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "Old task title"},
        headers=auth_headers,
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/tasks/{task_id}",
        json={"title": "New task title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New task title"


def test_toggle_task_done(client, auth_headers, project_id):
    create_response = client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "Toggle me"},
        headers=auth_headers,
    )
    task_id = create_response.json()["id"]
    assert create_response.json()["is_done"] is False

    toggle_response = client.patch(
        f"/projects/{project_id}/tasks/{task_id}/toggle", headers=auth_headers
    )
    assert toggle_response.status_code == 200
    assert toggle_response.json()["is_done"] is True

    toggle_again = client.patch(
        f"/projects/{project_id}/tasks/{task_id}/toggle", headers=auth_headers
    )
    assert toggle_again.json()["is_done"] is False


def test_delete_task(client, auth_headers, project_id):
    create_response = client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "To be deleted"},
        headers=auth_headers,
    )
    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/projects/{project_id}/tasks/{task_id}", headers=auth_headers
    )
    assert delete_response.status_code == 204

    list_response = client.get(f"/projects/{project_id}/tasks/", headers=auth_headers)
    assert list_response.json() == []


def test_cannot_create_task_in_other_users_project(client, project_id):
    client.post(
        "/auth/register",
        json={"email": "intruder@example.com", "password": "intruderpass123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "intruder@example.com", "password": "intruderpass123"},
    )
    token = login_response.json()["access_token"]
    headers_intruder = {"Authorization": f"Bearer {token}"}

    response = client.post(
        f"/projects/{project_id}/tasks/",
        json={"title": "Sneaky task"},
        headers=headers_intruder,
    )
    assert response.status_code == 404

def test_generate_tasks_from_text(client, auth_headers, project_id):
    fake_tasks = [
        TaskCreate(title="Call the client", description=None),
        TaskCreate(title="Send the invoice", description="Friday"),
    ]

    with patch(
        "app.services.task_service.LLMService.parse_tasks_from_text",
        return_value=fake_tasks,
    ): 
        response = client.post(
            f"/projects/{project_id}/tasks/generate",
            json={"text": "I need tp call the client and send the invoice by friday"},
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Call the client"
    assert data[1]["description"] == "Friday"

def test_generate_tasks_require_project_ownership(client, project_id):
    fake_tasks =[TaskCreate(title="Sneaky task", description=None)]

    client.post(
        "/auth/register",
        json={"email": "intruder2@example.com", "password": "intruderpass123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "intruder2@example.com", "password": "intruderpass123"},
    )
    token = login_response.json()["access_token"]
    headers_intruder = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.services.task_service.LLMService.parse_tasks_from_text",
        return_value=fake_tasks
    ):
        response = client.post(
            f"/projects/{project_id}/tasks/generate",
            json={"text": "anything"},
            headers=headers_intruder
        )

    assert response.status_code == 404
        
def test_search_tasks_requires_project_ownership(client, project_id):
    client.post(
        "/auth/register",
        json={"email": "intruder3@example.com", "password": "intruderpass123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "intruder3@example.com", "password": "intruderpass123"},
    )

    token = login_response.json()["access_token"]
    headers_intruder = {"Authorization": f"Bearer {token}"}

    response = client.get(
        f"/projects/{project_id}/tasks/search",
        params={"q": "anything"},
        headers=headers_intruder,
    )

    assert response.status_code == 404
