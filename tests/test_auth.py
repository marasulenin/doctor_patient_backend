
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_valid_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "pytestuser",
            "email": "pytestuser@example.com",
            "password": "Test@123",
            "role": "doctor"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == "pytestuser"
    assert data["user"]["email"] == "pytestuser@example.com"
    assert data["user"]["role"] == "doctor"


def test_register_weak_password():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "weakpassword",
            "email": "weakpassword@example.com",
            "password": "password",
            "role": "doctor"
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert "Password must be at least 8 characters" in data["detail"]


def test_register_duplicate_email():
    email = "duplicate@example.com"

    first_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicateone",
            "email": email,
            "password": "Test@123",
            "role": "doctor"
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicatetwo",
            "email": email,
            "password": "Test@123",
            "role": "doctor"
        }
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"


def test_login_valid_user():
    email = "loginpytest@example.com"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "loginpytest",
            "email": email,
            "password": "Test@123",
            "role": "doctor"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "Test@123"
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password():
    email = "invalidlogin@example.com"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "invalidlogin",
            "email": email,
            "password": "Test@123",
            "role": "doctor"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "Wrong@123"
        }
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"


def test_protected_endpoint_without_token():
    response = client.get(
        "/api/v1/protected"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

