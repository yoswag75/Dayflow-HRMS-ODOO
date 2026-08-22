import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_hash_and_verify():
    h = hash_password("secret")
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip():
    token = create_access_token({"sub": "1", "role": "EMPLOYEE"})
    data = decode_token(token)
    assert data["sub"] == "1"
    assert data["role"] == "EMPLOYEE"


def test_expired_token_raises():
    token = create_access_token({"sub": "1"}, expires_minutes=-1)
    with pytest.raises(Exception):
        decode_token(token)
