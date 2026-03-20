import pytest

def test_login_with_username_success(client, viewer_user):
    response = client.post(
        "/auth/login",
        data={"username": "viewer1", "password": "Password123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "viewer1"
    assert data["user"]["role"] == "viewer"


def test_login_with_email_success(client, viewer_user):
    response = client.post(
        "/auth/login",
        data={"username": "viewer@test.com", "password": "Password123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["user"]["email"] == "viewer@test.com"


def test_login_wrong_password_returns_401(client, viewer_user):
    response = client.post(
        "/auth/login",
        data={"username": "viewer1", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username/email or password"


def test_login_unknown_user_returns_401(client):
    response = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "Password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username/email or password"


def test_auth_me_returns_current_user(client, viewer_headers, viewer_user):
    response = client.get("/auth/me", headers=viewer_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "viewer1"
    assert data["email"] == "viewer@test.com"
    assert data["role"] == "viewer"


def test_auth_me_without_token_returns_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_auth_me_with_invalid_token_returns_401(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_inactive_user_cannot_access_me(client, db_session, viewer_user):
    viewer_user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "viewer1", "password": "Password123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 403
    assert me_response.json()["detail"] == "Inactive user"


def test_register_duplicate_username_returns_409(client, viewer_user):
    response = client.post(
        "/auth/register",
        json={
            "username": "viewer1",
            "email": "other@test.com",
            "password": "Password123",
            "role": "viewer",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "username already exists"


def test_register_duplicate_email_returns_409(client, viewer_user):
    response = client.post(
        "/auth/register",
        json={
            "username": "differentuser",
            "email": "viewer@test.com",
            "password": "Password123",
            "role": "viewer",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "email already exists"


def test_register_invalid_email_returns_422(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "not-an-email",
            "password": "Password123",
            "role": "viewer",
        },
    )
    assert response.status_code == 422


def test_register_short_password_returns_422(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "short",
            "role": "viewer",
        },
    )
    assert response.status_code == 422


def test_register_invalid_role_returns_422(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "Password123",
            "role": "superadmin",
        },
    )
    assert response.status_code == 422

def test_register_user_success_defaults_to_viewer(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "Password123",
            "role": "admin",
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "viewer"

def test_auth_me_with_wrong_auth_scheme_returns_401(client, viewer_headers):
    token = viewer_headers["Authorization"].split(" ", 1)[1]
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Token {token}"},
    )
    assert response.status_code == 401


def test_auth_me_with_empty_bearer_token_returns_401(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer "},
    )
    assert response.status_code == 401


def test_login_missing_password_returns_422(client):
    response = client.post(
        "/auth/login",
        data={"username": "viewer1"},
    )
    assert response.status_code == 422


def test_login_missing_username_returns_422(client):
    response = client.post(
        "/auth/login",
        data={"password": "Password123"},
    )
    assert response.status_code == 422


def test_register_missing_email_returns_422(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "Password123",
            "role": "viewer",
        },
    )
    assert response.status_code == 422


def test_register_missing_username_returns_422(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "Password123",
            "role": "viewer",
        },
    )
    assert response.status_code == 422