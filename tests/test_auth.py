import pytest
from backend.auth import verify_password, get_password_hash, create_access_token

def test_password_hashing():
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_logic():
    payload = {"sub": "testuser", "user_id": 123, "role": "admin"}
    token = create_access_token(data=payload, expires_delta=None)
    assert isinstance(token, str)
    
    # Import decode_token inside to avoid circular dependency if it exists
    from backend.auth import decode_token
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert decoded["user_id"] == 123
    assert decoded["role"] == "admin"
