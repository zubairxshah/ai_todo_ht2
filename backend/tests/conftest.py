import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"

from app.main import app
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def create_test_token(user_id: str) -> str:
    """Create a valid JWT token for testing."""
    from jose import jwt

    return jwt.encode(
        {"sub": user_id},
        os.environ["BETTER_AUTH_SECRET"],
        algorithm="HS256"
    )
