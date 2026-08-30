def test_register_new_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_login_returns_token(client):
    client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "supersecret123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_email_fails(client):
    client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "supersecret123"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "anotherpass123"},
    )
    assert response.status_code == 400


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "correctpass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword123"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user_fails(client):
    response = client.post(
        "/auth/login",
        json={"email": "doesnotexist@example.com", "password": "whatever12345"},
    )
    assert response.status_code == 401


def test_access_protected_route_without_token_fails(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    