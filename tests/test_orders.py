"""Tests for the Shop Order Management API (Task 23)."""


def test_create_order(client):
    """Create a purchase order for a shop product."""
    # Create a shop-type product first
    product = client.post("/api/products", params={
        "name": "Elegant Silk Saree",
        "price": 7990,
        "type": "shop",
    }).json()

    response = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Priya Sharma",
        "customer_phone": "+919876543210",
        "customer_email": "priya@example.com",
        "quantity": 2,
        "total_amount": 15980,
        "shipping_address": "123, Fashion Street, Mumbai",
        "notes": "Need for a wedding gift",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Priya Sharma"
    assert data["customer_phone"] == "+919876543210"
    assert data["customer_email"] == "priya@example.com"
    assert data["quantity"] == 2
    assert data["total_amount"] == 15980
    assert data["shipping_address"] == "123, Fashion Street, Mumbai"
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


def test_create_order_minimal(client):
    """Create an order with only required fields."""
    product = client.post("/api/products", params={
        "name": "Cotton Kurta Set",
        "price": 4500,
        "type": "shop",
    }).json()

    response = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Anita Patel",
        "customer_phone": "9876543210",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Anita Patel"
    assert data["quantity"] == 1  # default
    assert data["status"] == "pending"


def test_create_order_rental_product(client):
    """Ordering a rental product should be rejected."""
    product = client.post("/api/products", params={
        "name": "Rent Lehenga",
        "price": 3000,
        "type": "rent",
    }).json()

    response = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Test User",
        "customer_phone": "9876543210",
    })
    assert response.status_code == 400
    assert "only available for shop" in response.json()["detail"].lower()


def test_create_order_nonexistent_product(client):
    """Ordering a non-existent product should return 404."""
    response = client.post("/api/orders", json={
        "product_id": 99999,
        "customer_name": "Ghost User",
        "customer_phone": "9876543210",
    })
    assert response.status_code == 404


def test_list_orders_empty(client):
    """Should return empty list when no orders exist."""
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders_with_data(client):
    """Should list all orders after creation."""
    product = client.post("/api/products", params={
        "name": "Designer Saree",
        "price": 12500,
        "type": "shop",
    }).json()

    client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "User A",
        "customer_phone": "1111111111",
    })
    client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "User B",
        "customer_phone": "2222222222",
    })

    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [o["customer_name"] for o in data]
    assert "User A" in names
    assert "User B" in names


def test_list_orders_total_count_header(client):
    """Should return X-Total-Count header."""
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert "X-Total-Count" in response.headers


def test_list_orders_filter_by_status(client):
    """Should filter orders by status."""
    product = client.post("/api/products", params={
        "name": "Anarkali Suit",
        "price": 8900,
        "type": "shop",
    }).json()

    # Create one pending order
    order = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Pending User",
        "customer_phone": "3333333333",
    }).json()

    # Update to confirmed
    client.put(f"/api/orders/{order['id']}", json={"status": "confirmed"})

    # Create another pending order
    client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Another Pending",
        "customer_phone": "4444444444",
    })

    response = client.get("/api/orders", params={"status": "confirmed"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_name"] == "Pending User"

    response = client.get("/api/orders", params={"status": "pending"})
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_order_by_id(client):
    """Should retrieve a single order by ID."""
    product = client.post("/api/products", params={
        "name": "Embroidered Blouse",
        "price": 2500,
        "type": "shop",
    }).json()

    create = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Single Order",
        "customer_phone": "5555555555",
    }).json()

    response = client.get(f"/api/orders/{create['id']}")
    assert response.status_code == 200
    assert response.json()["customer_name"] == "Single Order"
    assert response.json()["product_id"] == product["id"]


def test_get_order_not_found(client):
    """Should return 404 for non-existent order."""
    response = client.get("/api/orders/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_update_order_status(client):
    """Should update order status."""
    product = client.post("/api/products", params={
        "name": "Lehenga Choli",
        "price": 18500,
        "type": "shop",
    }).json()

    create = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Status Update",
        "customer_phone": "6666666666",
    }).json()

    response = client.put(f"/api/orders/{create['id']}", json={
        "status": "confirmed",
        "notes": "Payment received",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["notes"] == "Payment received"


def test_update_order_partial(client):
    """Should partially update an order."""
    product = client.post("/api/products", params={
        "name": "Palazzo Set",
        "price": 3200,
        "type": "shop",
    }).json()

    create = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Partial Update",
        "customer_phone": "7777777777",
        "shipping_address": "Old Address",
    }).json()

    # Only update quantity and shipping address
    response = client.put(f"/api/orders/{create['id']}", json={
        "quantity": 3,
        "shipping_address": "New Address, Delhi",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 3
    assert data["shipping_address"] == "New Address, Delhi"
    assert data["customer_name"] == "Partial Update"  # unchanged


def test_update_order_not_found(client):
    """Should return 404 when updating non-existent order."""
    response = client.put("/api/orders/99999", json={"status": "confirmed"})
    assert response.status_code == 404


def test_delete_order(client):
    """Should delete an order and confirm."""
    product = client.post("/api/products", params={
        "name": "Casual Kurta",
        "price": 1500,
        "type": "shop",
    }).json()

    create = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Delete Me",
        "customer_phone": "8888888888",
    }).json()

    response = client.delete(f"/api/orders/{create['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify gone
    get_resp = client.get(f"/api/orders/{create['id']}")
    assert get_resp.status_code == 404


def test_delete_order_not_found(client):
    """Should return 404 when deleting non-existent order."""
    response = client.delete("/api/orders/99999")
    assert response.status_code == 404


def test_create_order_validation_errors(client):
    """Should reject invalid order data."""
    # Missing product_id
    response = client.post("/api/orders", json={
        "customer_name": "Test",
        "customer_phone": "1234567890",
    })
    assert response.status_code == 422

    # Missing required customer_name
    response = client.post("/api/orders", json={
        "product_id": 1,
        "customer_phone": "1234567890",
    })
    assert response.status_code == 422

    # Name too short
    product = client.post("/api/products", params={
        "name": "Shop Item",
        "price": 1000,
        "type": "shop",
    }).json()
    response = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "A",
        "customer_phone": "1234567890",
    })
    assert response.status_code == 422

    # Negative amount
    response = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Valid Name",
        "customer_phone": "1234567890",
        "total_amount": -100,
    })
    assert response.status_code == 422

    # Quantity zero
    response = client.post("/api/orders", json={
        "product_id": product["id"],
        "customer_name": "Valid Name",
        "customer_phone": "1234567890",
        "quantity": 0,
    })
    assert response.status_code == 422
