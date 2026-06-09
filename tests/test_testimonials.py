"""Tests for testimonials management API endpoints."""

import pytest


def test_list_testimonials_empty(client):
    """Should return empty list when no testimonials exist."""
    response = client.get("/api/testimonials")
    assert response.status_code == 200
    assert response.json() == []


def test_create_testimonial(client):
    """Should create a testimonial and return it with an ID."""
    payload = {
        "name": "Priya Sharma",
        "course": "1 Year Fashion Design",
        "review": "Amazing experience at Sujata Fashion!",
        "video_url": "https://youtube.com/watch?v=abc123",
        "rating": 5,
    }
    response = client.post("/api/testimonials", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Priya Sharma"
    assert data["course"] == "1 Year Fashion Design"
    assert data["rating"] == 5
    assert data["is_active"] == 1
    assert "id" in data


def test_list_testimonials_with_data(client):
    """Should list all testimonials after creation."""
    client.post("/api/testimonials", json={
        "name": "Alice", "course": "Blouse Design", "review": "Great!", "rating": 5,
    })
    client.post("/api/testimonials", json={
        "name": "Bob", "course": "Aari Work", "review": "Excellent!", "rating": 4,
    })

    response = client.get("/api/testimonials")
    assert response.status_code == 200
    testimonials = response.json()
    assert len(testimonials) == 2
    names = [t["name"] for t in testimonials]
    assert "Alice" in names
    assert "Bob" in names


def test_get_testimonial_by_id(client):
    """Should retrieve a single testimonial by its ID."""
    create_resp = client.post("/api/testimonials", json={
        "name": "Testimonial User",
        "course": "Fashion Design",
        "review": "Wonderful course!",
        "video_url": "https://youtube.com/watch?v=test123",
        "rating": 5,
    })
    testimonial_id = create_resp.json()["id"]

    response = client.get(f"/api/testimonials/{testimonial_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Testimonial User"
    assert response.json()["video_url"] == "https://youtube.com/watch?v=test123"


def test_get_testimonial_not_found(client):
    """Should return 404 for non-existent testimonial."""
    response = client.get("/api/testimonials/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Testimonial not found"


def test_update_testimonial(client):
    """Should update an existing testimonial's fields."""
    create_resp = client.post("/api/testimonials", json={
        "name": "Old Name",
        "course": "Old Course",
        "review": "Old review",
        "rating": 3,
    })
    testimonial_id = create_resp.json()["id"]

    response = client.put(f"/api/testimonials/{testimonial_id}", params={
        "name": "New Name",
        "review": "Updated review",
        "rating": 5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["review"] == "Updated review"
    assert data["rating"] == 5
    assert data["course"] == "Old Course"  # unchanged


def test_update_testimonial_not_found(client):
    """Should return 404 when updating non-existent testimonial."""
    response = client.put("/api/testimonials/99999", params={"name": "Ghost"})
    assert response.status_code == 404


def test_list_testimonials_active_only(client):
    """Should filter out inactive testimonials by default."""
    create_resp = client.post("/api/testimonials", json={
        "name": "To Deactivate",
        "course": "Course",
        "review": "Review",
    })
    testimonial_id = create_resp.json()["id"]

    # Deactivate
    client.put(f"/api/testimonials/{testimonial_id}", params={"is_active": False})

    # List should only show active by default
    response = client.get("/api/testimonials")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # List with active_only=False should show it
    response = client.get("/api/testimonials", params={"active_only": False})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_testimonial(client):
    """Should delete a testimonial and confirm."""
    create_resp = client.post("/api/testimonials", json={
        "name": "Delete Me",
        "course": "Course",
        "review": "Review",
    })
    testimonial_id = create_resp.json()["id"]

    response = client.delete(f"/api/testimonials/{testimonial_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify it's gone
    get_resp = client.get(f"/api/testimonials/{testimonial_id}")
    assert get_resp.status_code == 404


def test_delete_testimonial_not_found(client):
    """Should return 404 when deleting non-existent testimonial."""
    response = client.delete("/api/testimonials/99999")
    assert response.status_code == 404


def test_create_testimonial_validation(client):
    """Should reject invalid testimonial data."""
    # Missing required name
    response = client.post("/api/testimonials", json={
        "course": "Course",
    })
    assert response.status_code == 422

    # Name too short
    response = client.post("/api/testimonials", json={
        "name": "A",
        "course": "Course",
    })
    assert response.status_code == 422

    # Rating out of range
    response = client.post("/api/testimonials", json={
        "name": "Valid Name",
        "rating": 6,
    })
    assert response.status_code == 422
