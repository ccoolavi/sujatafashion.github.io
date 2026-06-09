"""Tests for the database seeding/data management endpoints."""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_connection, init_db


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure a clean database for each test."""
    # Ensure tables exist
    init_db()
    # Clear any existing data
    conn = get_connection()
    conn.execute("DELETE FROM products")
    conn.execute("DELETE FROM testimonials")
    conn.commit()
    conn.close()
    yield


client = TestClient(app)


class TestSeedEndpoint:
    """Tests for POST /api/seed — database seeding."""

    def test_seed_populates_products_and_testimonials(self):
        """Seeding should insert products and testimonials into the database."""
        response = client.post("/api/seed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["products_seeded"] > 0
        assert data["testimonials_seeded"] > 0

    def test_seed_is_idempotent_on_first_call(self):
        """Seeding should succeed on the first call (no error)."""
        response = client.post("/api/seed")
        assert response.status_code == 200
        first = response.json()
        assert first["products_seeded"] > 0
        assert first["testimonials_seeded"] > 0

    def test_seed_data_is_queryable_via_products_api(self):
        """After seeding, the products list API should return the seeded products."""
        client.post("/api/seed")
        response = client.get("/api/products")
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        assert any(p["name"] == "Elegant Silk Saree" for p in products)

    def test_seed_data_is_queryable_via_testimonials_api(self):
        """After seeding, the testimonials list API should return the seeded testimonials."""
        client.post("/api/seed")
        response = client.get("/api/testimonials")
        assert response.status_code == 200
        testimonials = response.json()
        assert len(testimonials) > 0
        assert any(t["name"] == "Priya Sharma" for t in testimonials)

    def test_seed_returns_correct_counts(self):
        """The seed response should contain the exact counts of inserted items."""
        response = client.post("/api/seed")
        data = response.json()
        assert data["products_seeded"] == 12  # 8 shop + 4 rent
        assert data["testimonials_seeded"] == 5


class TestClearSeedEndpoint:
    """Tests for DELETE /api/seed — clearing seed data."""

    def test_clear_removes_all_products_and_testimonials(self):
        """After clearing, products and testimonials tables should be empty."""
        client.post("/api/seed")
        clear_response = client.delete("/api/seed")
        assert clear_response.status_code == 200
        assert clear_response.json()["status"] == "success"

        # Verify products are empty
        products = client.get("/api/products").json()
        assert len(products) == 0

        # Verify testimonials are empty
        testimonials = client.get("/api/testimonials").json()
        assert len(testimonials) == 0

    def test_clear_on_empty_database_succeeds(self):
        """Clearing an already empty database should succeed gracefully."""
        response = client.delete("/api/seed")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_seed_after_clear_repopulates(self):
        """After a clear + seed, data should be repopulated."""
        client.post("/api/seed")
        client.delete("/api/seed")
        repost = client.post("/api/seed")
        assert repost.status_code == 200
        assert repost.json()["products_seeded"] == 12
