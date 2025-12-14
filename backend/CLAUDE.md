# Backend - Claude Code Rules

## Project Context

This is a FastAPI backend application using SQLModel ORM with Neon PostgreSQL.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL
- **Authentication**: JWT verification (python-jose)
- **Testing**: Pytest

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Settings and configuration
│   ├── database.py       # Database connection setup
│   ├── models/           # SQLModel database models
│   │   ├── user.py
│   │   └── task.py
│   ├── routers/          # API route handlers
│   │   └── tasks.py
│   ├── schemas/          # Pydantic request/response schemas
│   │   └── task.py
│   └── dependencies/     # Dependency injection
│       └── auth.py       # JWT verification
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── test_tasks.py
│   └── test_auth.py
├── requirements.txt
└── pyproject.toml
```

## Code Standards

### Python

- Follow PEP 8 style guide
- Use type hints for all functions
- Use async/await for I/O operations
- Keep functions focused and small

### FastAPI

- Use dependency injection for auth, db sessions
- Define Pydantic schemas for all request/response bodies
- Use appropriate HTTP status codes
- Document endpoints with docstrings

### SQLModel

- Define models with proper field constraints
- Use relationships for foreign keys
- Always filter queries by user_id for task operations

### Error Handling

- Use HTTPException for API errors
- Return appropriate status codes (400, 401, 403, 404, 500)
- Log errors for debugging
- Don't expose internal errors to clients

## Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
BETTER_AUTH_SECRET=<shared-secret>
```

## Commands

```bash
# Development
uvicorn app.main:app --reload    # Start dev server (port 8000)

# Testing
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest tests/test_tasks.py       # Run specific test file

# Dependencies
pip install -r requirements.txt  # Install dependencies
```

## API Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | /health | Health check | No |
| GET | /api/tasks | List user's tasks | Yes |
| POST | /api/tasks | Create a task | Yes |
| PATCH | /api/tasks/{id} | Update a task | Yes |
| DELETE | /api/tasks/{id} | Delete a task | Yes |

## Key Files

- `app/main.py` - Application setup, CORS, routers
- `app/dependencies/auth.py` - JWT verification logic
- `app/routers/tasks.py` - Task CRUD endpoints
- `app/models/task.py` - Task database model

## Security

- Verify JWT on all protected endpoints
- Always filter by user_id (never trust client-provided user_id)
- Use parameterized queries (SQLModel handles this)
- Load all secrets from environment variables
- Configure CORS for frontend origin only

## Testing

- Use pytest fixtures for database setup
- Mock JWT verification in tests
- Test both success and error cases
- Test user isolation (user A can't access user B's data)
