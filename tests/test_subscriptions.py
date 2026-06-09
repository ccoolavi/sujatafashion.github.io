"""Tests for the Newsletter Subscription API (Task 21)."""


def test_subscribe_new_email(client):
    """Subscribe a new email address."""
    response = client.post("/api/subscribe", json={
        "email": "test@example.com",
        "name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["is_active"] == 1
    assert data["source"] == "website"
    assert "id" in data


def test_subscribe_without_name(client):
    """Subscribe with just an email, no name."""
    response = client.post("/api/subscribe", json={
        "email": "anon@example.com",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "anon@example.com"
    assert data["name"] is None


def test_subscribe_duplicate_email(client):
    """Subscribing an existing email re-activates the subscription."""
    # First subscription
    response = client.post("/api/subscribe", json={
        "email": "dupe@example.com",
        "name": "First",
    })
    assert response.status_code == 201

    # Deactivate
    get_resp = client.get("/api/subscribers")
    sub_id = get_resp.json()[0]["id"]
    client.put(f"/api/subscribers/{sub_id}", json={"is_active": False})

    # Subscribe again — should re-activate
    response = client.post("/api/subscribe", json={
        "email": "dupe@example.com",
        "name": "Second",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] == 1
    # Name should be updated
    assert data["name"] == "Second"


def test_subscribe_invalid_email(client):
    """Subscribing with an invalid email returns 422."""
    response = client.post("/api/subscribe", json={
        "email": "not-an-email",
    })
    assert response.status_code == 422


def test_subscribe_missing_email(client):
    """Subscribing without an email returns 422."""
    response = client.post("/api/subscribe", json={})
    assert response.status_code == 422


def test_list_subscribers_empty(client):
    """Listing subscribers when none exist returns empty list."""
    response = client.get("/api/subscribers")
    assert response.status_code == 200
    assert response.json() == []


def test_list_subscribers_with_data(client):
    """Listing subscribers returns all entries."""
    client.post("/api/subscribe", json={"email": "a@example.com"})
    client.post("/api/subscribe", json={"email": "b@example.com"})
    response = client.get("/api/subscribers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_subscribers_active_only(client):
    """Listing active_only filter returns only active subscribers."""
    client.post("/api/subscribe", json={"email": "active@example.com"})
    client.post("/api/subscribe", json={"email": "inactive@example.com"})
    subs = client.get("/api/subscribers").json()
    inactive_id = subs[1]["id"]  # Second one
    client.put(f"/api/subscribers/{inactive_id}", json={"is_active": False})

    response = client.get("/api/subscribers?active_only=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "active@example.com"


def test_get_subscriber_by_id(client):
    """Get a single subscriber by ID."""
    create = client.post("/api/subscribe", json={
        "email": "getme@example.com",
        "name": "Getter",
    }).json()
    response = client.get(f"/api/subscribers/{create['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "getme@example.com"


def test_get_subscriber_not_found(client):
    """Get a non-existent subscriber returns 404."""
    response = client.get("/api/subscribers/999")
    assert response.status_code == 404


def test_update_subscriber_name(client):
    """Update a subscriber's name."""
    create = client.post("/api/subscribe", json={
        "email": "update@example.com",
    }).json()
    response = client.put(f"/api/subscribers/{create['id']}", json={
        "name": "Updated Name",
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_update_subscriber_deactivate(client):
    """Deactivate a subscriber."""
    create = client.post("/api/subscribe", json={
        "email": "deactivate@example.com",
    }).json()
    response = client.put(f"/api/subscribers/{create['id']}", json={
        "is_active": False,
    })
    assert response.status_code == 200
    assert response.json()["is_active"] == 0


def test_update_subscriber_not_found(client):
    """Update a non-existent subscriber returns 404."""
    response = client.put("/api/subscribers/999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_subscriber(client):
    """Delete a subscriber."""
    create = client.post("/api/subscribe", json={
        "email": "delete@example.com",
    }).json()
    response = client.delete(f"/api/subscribers/{create['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify gone
    get_resp = client.get(f"/api/subscribers/{create['id']}")
    assert get_resp.status_code == 404


def test_delete_subscriber_not_found(client):
    """Delete a non-existent subscriber returns 404."""
    response = client.delete("/api/subscribers/999")
    assert response.status_code == 404
