import pytest
from backend.main import app

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Sujata Fashion API is running"}

def test_register_user(client):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"

def test_duplicate_registration(client):
    user_data = {
        "email": "dup@example.com",
        "username": "dupuser",
        "password": "password123",
        "full_name": "Duplicate User"
    }
    # First registration
    client.post("/api/auth/register", json=user_data)
    # Second registration (same email/username)
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email or username already registered"

def test_login_success(client):
    # 1. Register a user
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "password123",
        "full_name": "Login User"
    }
    client.post("/api/auth/register", json=user_data)

    # 2. Login
    login_data = {
        "username": "loginuser",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(client):
    login_data = {
        "username": "nonexistent",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

def test_create_inquiry(client):
    """Submit a new inquiry via JSON body."""
    inquiry_data = {
        "name": "John Doe",
        "phone": "1234567890",
        "email": "john@example.com",
        "course": "Styling 101",
        "message": "Interested in the course."
    }
    response = client.post("/api/inquiries", json=inquiry_data)
    assert response.status_code == 201
    assert response.json()["status"] == "ok"
    assert "id" in response.json()


def test_create_inquiry_validation(client):
    """Should reject invalid inquiry data (missing required fields, bad email)."""
    # Missing required name
    response = client.post("/api/inquiries", json={
        "phone": "1234567890",
        "email": "john@example.com"
    })
    assert response.status_code == 422

    # Invalid email
    response = client.post("/api/inquiries", json={
        "name": "John",
        "phone": "1234567890",
        "email": "not-an-email"
    })
    assert response.status_code == 422

    # Name too short
    response = client.post("/api/inquiries", json={
        "name": "J",
        "phone": "1234567890",
        "email": "john@example.com"
    })
    assert response.status_code == 422
