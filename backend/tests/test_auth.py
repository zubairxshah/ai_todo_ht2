import os
import pytest
from jose import jwt

from app.dependencies.auth import get_current_user_id
from fastapi import HTTPException


def test_get_current_user_id_valid_token():
    """Test that valid JWT token returns user ID."""
    user_id = "test-user-123"
    token = jwt.encode(
        {"sub": user_id},
        os.environ["BETTER_AUTH_SECRET"],
        algorithm="HS256"
    )

    result = get_current_user_id(f"Bearer {token}")
    assert result == user_id


def test_get_current_user_id_invalid_format():
    """Test that invalid authorization format raises error."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id("InvalidFormat token")

    assert exc_info.value.status_code == 401
    assert "Invalid authorization header format" in exc_info.value.detail


def test_get_current_user_id_invalid_token():
    """Test that invalid token raises error."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id("Bearer invalid-token")

    assert exc_info.value.status_code == 401


def test_get_current_user_id_missing_sub():
    """Test that token without sub claim raises error."""
    token = jwt.encode(
        {"other": "data"},
        os.environ["BETTER_AUTH_SECRET"],
        algorithm="HS256"
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(f"Bearer {token}")

    assert exc_info.value.status_code == 401
    assert "missing user ID" in exc_info.value.detail


def test_get_current_user_id_wrong_secret():
    """Test that token signed with wrong secret is rejected."""
    token = jwt.encode(
        {"sub": "user-id"},
        "wrong-secret",
        algorithm="HS256"
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(f"Bearer {token}")

    assert exc_info.value.status_code == 401
