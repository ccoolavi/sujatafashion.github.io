"""Tests for the Wishlist / Favorites API."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_connection, init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Reset the database before each test and seed a product."""
    init_db()
    conn = get_connection()
    # Ensure a product exists for wishlist tests
    conn.execute("DELETE FROM wishlist")
    conn.execute("DELETE FROM products")
    conn.execute(
        """INSERT INTO products (id, name, category, price, description, type)
           VALUES (1, 'Test Product', 'C1', 1000, 'A test product', 'shop')"""
    )
    conn.commit()
    conn.close()
    yield


class TestWishlistAPI:
    """Test suite for the Wishlist CRUD API."""

    WISHLIST_ENDPOINT = "/api/wishlist"

    def test_create_wishlist_item(self):
        """Test adding a product to the wishlist."""
        response = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1,
            "customer_name": "Priya Sharma",
            "customer_phone": "9876543210",
            "customer_email": "priya@example.com",
            "notes": "Love this product!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == 1
        assert data["customer_name"] == "Priya Sharma"
        assert data["customer_phone"] == "9876543210"
        assert data["customer_email"] == "priya@example.com"
        assert data["notes"] == "Love this product!"
        assert "id" in data
        assert "created_at" in data

    def test_create_wishlist_with_minimal_fields(self):
        """Test adding to wishlist with only required fields."""
        response = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1,
            "customer_name": "Anita Patel",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "Anita Patel"
        assert data["customer_phone"] is None
        assert data["customer_email"] is None
        assert data["notes"] is None

    def test_create_wishlist_nonexistent_product(self):
        """Test that adding a non-existent product returns 404."""
        response = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 999,
            "customer_name": "Test User",
        })
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    def test_create_duplicate_wishlist_item(self):
        """Test that duplicate wishlist entry returns 409."""
        payload = {
            "product_id": 1,
            "customer_name": "Priya Sharma",
            "customer_phone": "9876543210",
            "customer_email": "priya@example.com",
        }
        # First creation should succeed
        response1 = client.post(self.WISHLIST_ENDPOINT, json=payload)
        assert response1.status_code == 201

        # Duplicate should fail with 409
        response2 = client.post(self.WISHLIST_ENDPOINT, json=payload)
        assert response2.status_code == 409
        assert "already in your wishlist" in response2.json()["detail"]

    def test_create_wishlist_invalid_name(self):
        """Test that too short name is rejected."""
        response = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1,
            "customer_name": "A",
        })
        assert response.status_code == 422

    def test_create_wishlist_invalid_product_id(self):
        """Test that missing product_id is rejected."""
        response = client.post(self.WISHLIST_ENDPOINT, json={
            "customer_name": "Test User",
        })
        assert response.status_code == 422

    def test_list_wishlist(self):
        """Test listing all wishlist items."""
        # Create two items
        client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "User One",
            "customer_phone": "1111111111",
        })
        client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "User Two",
            "customer_phone": "2222222222",
        })

        response = client.get(self.WISHLIST_ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Verify X-Total-Count header
        assert response.headers.get("X-Total-Count") == "2"

    def test_list_wishlist_pagination(self):
        """Test pagination of wishlist items."""
        # Create 3 items
        for i in range(3):
            client.post(self.WISHLIST_ENDPOINT, json={
                "product_id": 1, "customer_name": f"User {i}",
                "customer_phone": f"000000000{i}",
            })

        # Get with limit 2
        response = client.get(f"{self.WISHLIST_ENDPOINT}?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert response.headers.get("X-Total-Count") == "3"

    def test_get_single_wishlist_item(self):
        """Test retrieving a single wishlist item by ID."""
        create_resp = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "Test User",
        })
        item_id = create_resp.json()["id"]

        response = client.get(f"{self.WISHLIST_ENDPOINT}/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["customer_name"] == "Test User"

    def test_get_nonexistent_wishlist_item(self):
        """Test retrieving a non-existent wishlist item returns 404."""
        response = client.get(f"{self.WISHLIST_ENDPOINT}/999")
        assert response.status_code == 404
        assert "Wishlist item not found" in response.json()["detail"]

    def test_update_wishlist_item(self):
        """Test updating a wishlist item."""
        create_resp = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "Original Name",
            "notes": "Original note",
        })
        item_id = create_resp.json()["id"]

        response = client.put(f"{self.WISHLIST_ENDPOINT}/{item_id}", json={
            "customer_name": "Updated Name",
            "notes": "Updated note",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "Updated Name"
        assert data["notes"] == "Updated note"
        assert data["id"] == item_id

    def test_update_nonexistent_wishlist_item(self):
        """Test updating a non-existent item returns 404."""
        response = client.put(f"{self.WISHLIST_ENDPOINT}/999", json={
            "customer_name": "New Name",
        })
        assert response.status_code == 404

    def test_delete_wishlist_item(self):
        """Test removing an item from the wishlist."""
        create_resp = client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "Delete Me",
        })
        item_id = create_resp.json()["id"]

        response = client.delete(f"{self.WISHLIST_ENDPOINT}/{item_id}")
        assert response.status_code == 200
        assert response.json()["deleted_id"] == item_id

        # Verify it's gone
        get_resp = client.get(f"{self.WISHLIST_ENDPOINT}/{item_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_wishlist_item(self):
        """Test deleting a non-existent item returns 404."""
        response = client.delete(f"{self.WISHLIST_ENDPOINT}/999")
        assert response.status_code == 404

    def test_find_wishlist_by_phone(self):
        """Test finding wishlist items by phone number."""
        client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "Phone User",
            "customer_phone": "9876543210",
        })

        response = client.get(f"{self.WISHLIST_ENDPOINT}/find?customer_phone=9876543210")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["customer_phone"] == "9876543210"

    def test_find_wishlist_by_email(self):
        """Test finding wishlist items by email."""
        client.post(self.WISHLIST_ENDPOINT, json={
            "product_id": 1, "customer_name": "Email User",
            "customer_email": "user@example.com",
        })

        response = client.get(f"{self.WISHLIST_ENDPOINT}/find?customer_email=user@example.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["customer_email"] == "user@example.com"

    def test_find_wishlist_no_match(self):
        """Test finding with no matches returns empty list."""
        response = client.get(f"{self.WISHLIST_ENDPOINT}/find?customer_phone=nonexistent")
        assert response.status_code == 200
        assert response.json() == []
