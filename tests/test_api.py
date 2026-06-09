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


def test_upload_image_success(client):
    """Should upload an image and return Cloudinary URL."""
    import io
    from unittest.mock import patch

    mock_result = {
        "secure_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/test.jpg",
        "public_id": "sfa_assets/test",
        "format": "jpg",
        "width": 800,
        "height": 600,
    }

    with patch("cloudinary.uploader.upload", return_value=mock_result):
        test_file = io.BytesIO(b"fake-image-bytes")
        test_file.name = "test.jpg"
        response = client.post(
            "/api/upload",
            files={"file": ("test.jpg", test_file, "image/jpeg")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["url"] == mock_result["secure_url"]
    assert data["public_id"] == mock_result["public_id"]
    assert data["format"] == "jpg"


def test_upload_image_rejects_non_image(client):
    """Should reject non-image file uploads."""
    import io

    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Only image files" in response.json()["detail"]


# --- Inquiry Management Tests (Task 20) ---


def test_get_single_inquiry(client):
    """Should retrieve a single inquiry by ID."""
    # Create an inquiry first
    inquiry_data = {
        "name": "Test User",
        "phone": "9876543210",
        "email": "test@example.com",
        "course": "Fashion Design",
        "message": "Interested in the course.",
    }
    create_resp = client.post("/api/inquiries", json=inquiry_data)
    inquiry_id = create_resp.json()["id"]

    # Retrieve it
    response = client.get(f"/api/inquiries/{inquiry_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["status"] == "new"


def test_get_inquiry_not_found(client):
    """Should return 404 for non-existent inquiry."""
    response = client.get("/api/inquiries/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inquiry not found"


def test_update_inquiry_status(client):
    """Should update inquiry status and notes."""
    create_resp = client.post("/api/inquiries", json={
        "name": "Status Test",
        "phone": "1111111111",
        "email": "status@example.com",
        "course": "Makeup Artistry",
    })
    inquiry_id = create_resp.json()["id"]

    response = client.put(f"/api/inquiries/{inquiry_id}", json={
        "status": "contacted",
        "notes": "Called customer, interested in weekend batch",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "contacted"
    assert data["notes"] == "Called customer, interested in weekend batch"


def test_update_inquiry_partial(client):
    """Should allow partial update of inquiry fields."""
    create_resp = client.post("/api/inquiries", json={
        "name": "Partial Test",
        "phone": "2222222222",
        "email": "partial@example.com",
        "course": "Original Course",
    })
    inquiry_id = create_resp.json()["id"]

    # Update only the course
    response = client.put(f"/api/inquiries/{inquiry_id}", json={
        "course": "Updated Course",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["course"] == "Updated Course"
    assert data["name"] == "Partial Test"  # Unchanged


def test_update_inquiry_not_found(client):
    """Should return 404 when updating non-existent inquiry."""
    response = client.put("/api/inquiries/99999", json={"status": "contacted"})
    assert response.status_code == 404


def test_delete_inquiry(client):
    """Should delete an inquiry by ID."""
    create_resp = client.post("/api/inquiries", json={
        "name": "Delete Test",
        "phone": "3333333333",
        "email": "delete@example.com",
    })
    inquiry_id = create_resp.json()["id"]

    # Delete it
    response = client.delete(f"/api/inquiries/{inquiry_id}")
    assert response.status_code == 200
    assert response.json()["deleted_id"] == inquiry_id

    # Verify it's gone
    get_resp = client.get(f"/api/inquiries/{inquiry_id}")
    assert get_resp.status_code == 404


def test_delete_inquiry_not_found(client):
    """Should return 404 when deleting non-existent inquiry."""
    response = client.delete("/api/inquiries/99999")
    assert response.status_code == 404
