import time
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException, status

from app.config import settings


# Cache for JWKS client
_jwks_client: PyJWKClient | None = None
_jwks_client_time: float = 0
JWKS_CACHE_TTL = 3600  # 1 hour cache


def get_jwks_client() -> PyJWKClient:
    """Get or create a JWKS client with caching."""
    global _jwks_client, _jwks_client_time

    current_time = time.time()
    if _jwks_client and (current_time - _jwks_client_time) < JWKS_CACHE_TTL:
        return _jwks_client

    jwks_url = f"{settings.AUTH_URL}/api/auth/jwks"
    _jwks_client = PyJWKClient(jwks_url)
    _jwks_client_time = current_time
    return _jwks_client


async def get_current_user_id(authorization: str = Header(...)) -> str:
    """
    Extract and verify user ID from JWT token.
    The token is expected in format: "Bearer <token>"
    Verifies token using JWKS from Better Auth.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "RS256", "ES256"],
            options={"verify_aud": False},  # Better Auth doesn't set audience by default
        )

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
        )
