def test_create_project(client, auth_headers):
    response = client.post(
        "/projects/",
        json={"title": "My Project", "description": "A test project"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Project"
    assert "id" in data


def test_list_projects(client, auth_headers):
    client.post("/projects/", json={"title": "Project 1"}, headers=auth_headers)
    client.post("/projects/", json={"title": "Project 2"}, headers=auth_headers)

    response = client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_single_project(client, auth_headers):
    create_response = client.post(
        "/projects/", json={"title": "Solo Project"}, headers=auth_headers
    )
    project_id = create_response.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Solo Project"


def test_update_project(client, auth_headers):
    create_response = client.post(
        "/projects/", json={"title": "Old Title"}, headers=auth_headers
    )
    project_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={"title": "New Title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_project(client, auth_headers):
    create_response = client.post(
        "/projects/", json={"title": "To Delete"}, headers=auth_headers
    )
    project_id = create_response.json()["id"]

    delete_response = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_cannot_access_other_users_project(client):
    client.post(
        "/auth/register",
        json={"email": "userA@example.com", "password": "passwordA123"},
    )
    login_a = client.post(
        "/auth/login",
        json={"email": "userA@example.com", "password": "passwordA123"},
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    create_response = client.post(
        "/projects/", json={"title": "User A's Project"}, headers=headers_a
    )
    project_id = create_response.json()["id"]

    client.post(
        "/auth/register",
        json={"email": "userB@example.com", "password": "passwordB123"},
    )
    login_b = client.post(
        "/auth/login",
        json={"email": "userB@example.com", "password": "passwordB123"},
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    response = client.get(f"/projects/{project_id}", headers=headers_b)
    assert response.status_code == 404