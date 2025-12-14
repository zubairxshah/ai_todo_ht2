import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User
from app.models.task import Task
from tests.conftest import create_test_token


def test_list_tasks_empty(client: TestClient, session: Session):
    """Test listing tasks when user has none."""
    # Create test user
    user = User(id="user-1", email="test@example.com")
    session.add(user)
    session.commit()

    token = create_test_token("user-1")
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_only_user_tasks(client: TestClient, session: Session):
    """Test that users can only see their own tasks."""
    # Create two users
    user1 = User(id="user-1", email="user1@example.com")
    user2 = User(id="user-2", email="user2@example.com")
    session.add(user1)
    session.add(user2)

    # Create tasks for both users
    task1 = Task(id="task-1", title="User 1 Task", user_id="user-1")
    task2 = Task(id="task-2", title="User 2 Task", user_id="user-2")
    session.add(task1)
    session.add(task2)
    session.commit()

    # User 1 should only see their task
    token = create_test_token("user-1")
    response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "User 1 Task"


def test_create_task(client: TestClient, session: Session):
    """Test creating a new task."""
    user = User(id="user-1", email="test@example.com")
    session.add(user)
    session.commit()

    token = create_test_token("user-1")
    response = client.post(
        "/api/tasks",
        json={"title": "New Task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["completed"] is False
    assert "id" in data


def test_create_task_empty_title_fails(client: TestClient, session: Session):
    """Test that creating a task with empty title fails validation."""
    user = User(id="user-1", email="test@example.com")
    session.add(user)
    session.commit()

    token = create_test_token("user-1")
    response = client.post(
        "/api/tasks",
        json={"title": ""},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422


def test_update_task(client: TestClient, session: Session):
    """Test updating a task."""
    user = User(id="user-1", email="test@example.com")
    task = Task(id="task-1", title="Original Title", user_id="user-1")
    session.add(user)
    session.add(task)
    session.commit()

    token = create_test_token("user-1")
    response = client.patch(
        "/api/tasks/task-1",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True


def test_update_task_forbidden_for_other_user(client: TestClient, session: Session):
    """Test that users cannot update other users' tasks."""
    user1 = User(id="user-1", email="user1@example.com")
    user2 = User(id="user-2", email="user2@example.com")
    task = Task(id="task-1", title="User 1 Task", user_id="user-1")
    session.add(user1)
    session.add(user2)
    session.add(task)
    session.commit()

    # User 2 tries to update User 1's task
    token = create_test_token("user-2")
    response = client.patch(
        "/api/tasks/task-1",
        json={"title": "Hacked!"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_delete_task(client: TestClient, session: Session):
    """Test deleting a task."""
    user = User(id="user-1", email="test@example.com")
    task = Task(id="task-1", title="To Delete", user_id="user-1")
    session.add(user)
    session.add(task)
    session.commit()

    token = create_test_token("user-1")
    response = client.delete(
        "/api/tasks/task-1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204


def test_delete_task_forbidden_for_other_user(client: TestClient, session: Session):
    """Test that users cannot delete other users' tasks."""
    user1 = User(id="user-1", email="user1@example.com")
    user2 = User(id="user-2", email="user2@example.com")
    task = Task(id="task-1", title="User 1 Task", user_id="user-1")
    session.add(user1)
    session.add(user2)
    session.add(task)
    session.commit()

    # User 2 tries to delete User 1's task
    token = create_test_token("user-2")
    response = client.delete(
        "/api/tasks/task-1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_unauthorized_request(client: TestClient):
    """Test that requests without auth fail."""
    response = client.get("/api/tasks")
    assert response.status_code == 422  # Missing header


def test_invalid_token(client: TestClient):
    """Test that invalid tokens are rejected."""
    response = client.get(
        "/api/tasks",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
