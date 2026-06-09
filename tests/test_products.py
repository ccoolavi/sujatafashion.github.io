"""Tests for product management API endpoints."""

import pytest


def test_list_products_empty(client):
    """Should return empty list when no products exist."""
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product(client):
    """Should create a product and return it with an ID."""
    params = {
        "name": "Test Lehenga",
        "category": "Wedding",
        "price": 25000,
        "description": "Beautiful wedding lehenga",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/test.jpg",
        "type": "shop",
    }
    response = client.post("/api/products", params=params)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Lehenga"
    assert data["category"] == "Wedding"
    assert data["price"] == 25000
    assert data["type"] == "shop"
    assert data["is_active"] == 1
    assert "id" in data


def test_list_products_with_data(client):
    """Should list all products after creation."""
    # Create two products
    client.post("/api/products", params={
        "name": "Product A",
        "category": "Casual",
        "price": 1500,
        "type": "shop",
    })
    client.post("/api/products", params={
        "name": "Product B",
        "category": "Formal",
        "price": 5000,
        "type": "rent",
    })

    response = client.get("/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 2
    names = [p["name"] for p in products]
    assert "Product A" in names
    assert "Product B" in names


def test_list_products_filter_by_category(client):
    """Should filter products by category."""
    client.post("/api/products", params={
        "name": "Wedding Dress",
        "category": "Wedding",
        "price": 50000,
        "type": "shop",
    })
    client.post("/api/products", params={
        "name": "Casual Saree",
        "category": "Casual",
        "price": 2000,
        "type": "shop",
    })

    response = client.get("/api/products", params={"category": "Wedding"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Wedding Dress"


def test_list_products_filter_by_type(client):
    """Should filter products by type (shop vs rent)."""
    client.post("/api/products", params={
        "name": "Shop Item",
        "price": 1000,
        "type": "shop",
    })
    client.post("/api/products", params={
        "name": "Rent Item",
        "price": 500,
        "type": "rent",
    })

    response = client.get("/api/products", params={"type": "rent"})
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Rent Item"


def test_get_product_by_id(client):
    """Should retrieve a single product by its ID."""
    create_resp = client.post("/api/products", params={
        "name": "Silk Saree",
        "price": 12000,
        "type": "shop",
    })
    product_id = create_resp.json()["id"]

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Silk Saree"


def test_get_product_not_found(client):
    """Should return 404 for non-existent product."""
    response = client.get("/api/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product(client):
    """Should update an existing product's fields."""
    create_resp = client.post("/api/products", params={
        "name": "Old Name",
        "price": 1000,
        "type": "shop",
    })
    product_id = create_resp.json()["id"]

    response = client.put(f"/api/products/{product_id}", params={
        "name": "New Name",
        "price": 2000,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["price"] == 2000


def test_update_product_not_found(client):
    """Should return 404 when updating non-existent product."""
    response = client.put("/api/products/99999", params={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_product(client):
    """Should delete a product and confirm."""
    create_resp = client.post("/api/products", params={
        "name": "Delete Me",
        "price": 500,
        "type": "shop",
    })
    product_id = create_resp.json()["id"]

    response = client.delete(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify it's gone
    get_resp = client.get(f"/api/products/{product_id}")
    assert get_resp.status_code == 404


def test_delete_product_not_found(client):
    """Should return 404 when deleting non-existent product."""
    response = client.delete("/api/products/99999")
    assert response.status_code == 404
