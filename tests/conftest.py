import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.database import init_db
import sqlite3
import os

# Path for the temporary test database
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_sujata.db")

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Sets up the test database before the session and cleans up after."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    with patch("backend.database.get_db_path", return_value=TEST_DB_PATH):
        init_db()
        yield
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

@pytest.fixture(scope="function")
def client():
    """Provides a TestClient for the FastAPI app, with database monkeypatching."""
    
    with patch("backend.main.get_connection") as mock_get_conn, \
         patch("backend.database.get_connection") as mock_db_get_conn:
        
        def test_get_connection():
            conn = sqlite3.connect(TEST_DB_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            return conn

        mock_get_conn.side_effect = test_get_connection
        mock_db_get_conn.side_effect = test_get_connection

        with TestClient(app) as c:
            yield c

@pytest.fixture(autouse=True)
def clear_tables(client):
    """Clears all tables before each test to ensure isolation."""
    with patch("backend.database.get_db_path", return_value=TEST_DB_PATH):
        import backend.database
        conn = backend.database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sessions")
        cursor.execute("DELETE FROM inquiries")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM testimonials")
        cursor.execute("DELETE FROM subscriptions")
        cursor.execute("DELETE FROM bookings")
        conn.commit()
        conn.close()
