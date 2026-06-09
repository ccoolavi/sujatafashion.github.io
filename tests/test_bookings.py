"""Tests for the Rental Booking Management API (Task 22)."""


def test_create_booking(client):
    """Create a rental booking for a rental product."""
    # Create a rent-type product first
    product = client.post("/api/products", params={
        "name": "Festival Lehenga",
        "price": 3000,
        "type": "rent",
    }).json()

    response = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Priya Sharma",
        "customer_phone": "+919876543210",
        "customer_email": "priya@example.com",
        "start_date": "2026-06-15",
        "end_date": "2026-06-20",
        "total_amount": 3000,
        "deposit_amount": 500,
        "notes": "Need for a wedding",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Priya Sharma"
    assert data["customer_phone"] == "+919876543210"
    assert data["customer_email"] == "priya@example.com"
    assert data["start_date"] == "2026-06-15"
    assert data["end_date"] == "2026-06-20"
    assert data["total_amount"] == 3000
    assert data["deposit_amount"] == 500
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


def test_create_booking_minimal(client):
    """Create a booking with only required fields."""
    product = client.post("/api/products", params={
        "name": "Rent Saree",
        "price": 2500,
        "type": "rent",
    }).json()

    response = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Anita Patel",
        "customer_phone": "9876543210",
        "start_date": "2026-07-01",
        "end_date": "2026-07-05",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Anita Patel"
    assert data["deposit_amount"] == 0  # default
    assert data["status"] == "pending"


def test_create_booking_shop_product(client):
    """Booking a shop product should be rejected."""
    product = client.post("/api/products", params={
        "name": "Shop Item",
        "price": 1000,
        "type": "shop",
    }).json()

    response = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Test User",
        "customer_phone": "9876543210",
        "start_date": "2026-06-01",
        "end_date": "2026-06-05",
    })
    assert response.status_code == 400
    assert "only available for rental" in response.json()["detail"].lower()


def test_create_booking_nonexistent_product(client):
    """Booking a non-existent product should return 404."""
    response = client.post("/api/bookings", json={
        "product_id": 99999,
        "customer_name": "Ghost User",
        "customer_phone": "9876543210",
        "start_date": "2026-06-01",
        "end_date": "2026-06-05",
    })
    assert response.status_code == 404


def test_list_bookings_empty(client):
    """Should return empty list when no bookings exist."""
    response = client.get("/api/bookings")
    assert response.status_code == 200
    assert response.json() == []


def test_list_bookings_with_data(client):
    """Should list all bookings after creation."""
    product = client.post("/api/products", params={
        "name": "Rent Gown",
        "price": 4000,
        "type": "rent",
    }).json()

    client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "User A",
        "customer_phone": "1111111111",
        "start_date": "2026-08-01",
        "end_date": "2026-08-03",
    })
    client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "User B",
        "customer_phone": "2222222222",
        "start_date": "2026-08-05",
        "end_date": "2026-08-07",
    })

    response = client.get("/api/bookings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [b["customer_name"] for b in data]
    assert "User A" in names
    assert "User B" in names


def test_list_bookings_total_count_header(client):
    """Should return X-Total-Count header."""
    response = client.get("/api/bookings")
    assert response.status_code == 200
    assert "X-Total-Count" in response.headers


def test_list_bookings_filter_by_status(client):
    """Should filter bookings by status."""
    product = client.post("/api/products", params={
        "name": "Rent Gown",
        "price": 4000,
        "type": "rent",
    }).json()

    # Create one pending booking
    booking = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Pending User",
        "customer_phone": "3333333333",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03",
    }).json()

    # Update to confirmed
    client.put(f"/api/bookings/{booking['id']}", json={"status": "confirmed"})

    # Create another pending booking
    client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Another Pending",
        "customer_phone": "4444444444",
        "start_date": "2026-09-05",
        "end_date": "2026-09-07",
    })

    response = client.get("/api/bookings", params={"status": "confirmed"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_name"] == "Pending User"

    response = client.get("/api/bookings", params={"status": "pending"})
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_booking_by_id(client):
    """Should retrieve a single booking by ID."""
    product = client.post("/api/products", params={
        "name": "Rent Lehenga",
        "price": 5000,
        "type": "rent",
    }).json()

    create = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Single Booking",
        "customer_phone": "5555555555",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
    }).json()

    response = client.get(f"/api/bookings/{create['id']}")
    assert response.status_code == 200
    assert response.json()["customer_name"] == "Single Booking"
    assert response.json()["product_id"] == product["id"]


def test_get_booking_not_found(client):
    """Should return 404 for non-existent booking."""
    response = client.get("/api/bookings/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_update_booking_status(client):
    """Should update booking status."""
    product = client.post("/api/products", params={
        "name": "Rent Saree",
        "price": 2500,
        "type": "rent",
    }).json()

    create = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Status Update",
        "customer_phone": "6666666666",
        "start_date": "2026-11-01",
        "end_date": "2026-11-05",
    }).json()

    response = client.put(f"/api/bookings/{create['id']}", json={
        "status": "confirmed",
        "notes": "Deposit received",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["notes"] == "Deposit received"


def test_update_booking_partial(client):
    """Should partially update a booking."""
    product = client.post("/api/products", params={
        "name": "Rent Gown",
        "price": 4000,
        "type": "rent",
    }).json()

    create = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Partial Update",
        "customer_phone": "7777777777",
        "start_date": "2026-12-01",
        "end_date": "2026-12-05",
    }).json()

    # Only update total_amount
    response = client.put(f"/api/bookings/{create['id']}", json={
        "total_amount": 3500,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_amount"] == 3500
    assert data["customer_name"] == "Partial Update"  # unchanged


def test_update_booking_not_found(client):
    """Should return 404 when updating non-existent booking."""
    response = client.put("/api/bookings/99999", json={"status": "confirmed"})
    assert response.status_code == 404


def test_delete_booking(client):
    """Should delete a booking and confirm."""
    product = client.post("/api/products", params={
        "name": "Rent Lehenga",
        "price": 5000,
        "type": "rent",
    }).json()

    create = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Delete Me",
        "customer_phone": "8888888888",
        "start_date": "2026-12-10",
        "end_date": "2026-12-15",
    }).json()

    response = client.delete(f"/api/bookings/{create['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify gone
    get_resp = client.get(f"/api/bookings/{create['id']}")
    assert get_resp.status_code == 404


def test_delete_booking_not_found(client):
    """Should return 404 when deleting non-existent booking."""
    response = client.delete("/api/bookings/99999")
    assert response.status_code == 404


def test_create_booking_validation_errors(client):
    """Should reject invalid booking data."""
    # Missing product_id
    response = client.post("/api/bookings", json={
        "customer_name": "Test",
        "customer_phone": "1234567890",
    })
    assert response.status_code == 422

    # Missing required customer_name
    response = client.post("/api/bookings", json={
        "product_id": 1,
        "customer_phone": "1234567890",
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
    })
    assert response.status_code == 422

    # Name too short
    product = client.post("/api/products", params={
        "name": "Rent Item",
        "price": 1000,
        "type": "rent",
    }).json()
    response = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "A",
        "customer_phone": "1234567890",
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
    })
    assert response.status_code == 422

    # Negative amount
    response = client.post("/api/bookings", json={
        "product_id": product["id"],
        "customer_name": "Valid Name",
        "customer_phone": "1234567890",
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
        "total_amount": -100,
    })
    assert response.status_code == 422
