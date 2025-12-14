# Implementation Plan: Todo App

**Branch**: `001-todo-app` | **Date**: 2025-12-14 | **Spec**: [spec.md](./spec.md)

## Summary

Full-stack Todo application with Next.js frontend (App Router, Tailwind CSS) and FastAPI backend (SQLModel, Neon PostgreSQL). Authentication via Better Auth with JWT plugin, sharing BETTER_AUTH_SECRET between frontend and backend for token verification. All task operations enforce user ownership.

## Technical Context

**Frontend**:
- Framework: Next.js 14+ (App Router)
- Language: TypeScript (strict mode)
- Styling: Tailwind CSS
- Auth: Better Auth client SDK
- HTTP Client: fetch API

**Backend**:
- Framework: FastAPI
- Language: Python 3.11+
- ORM: SQLModel
- Database: Neon PostgreSQL
- Auth: Better Auth JWT verification using shared secret
- Validation: Pydantic (via SQLModel)

**Testing**:
- Frontend: Jest + React Testing Library
- Backend: pytest + httpx

## Constitution Check

*GATE: Must pass before implementation*

- [x] **TDD**: Tests written before implementation
- [x] **Simplicity**: No unnecessary abstractions
- [x] **Security**: User ownership enforced, secrets in env vars
- [x] **Type Safety**: TypeScript strict, Python type hints

## Project Structure

### Documentation

```text
specs/todo-app/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Implementation tasks
```

### Source Code

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Landing/redirect
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── dashboard/page.tsx    # Task list
│   ├── components/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   └── TaskForm.tsx
│   ├── lib/
│   │   ├── auth.ts               # Better Auth client
│   │   └── api.ts                # Backend API client
│   └── types/
│       └── index.ts
├── tailwind.config.ts
├── next.config.js
├── package.json
└── .env.local

backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app
│   ├── config.py                 # Environment config
│   ├── database.py               # SQLModel + Neon connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tasks.py
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py               # JWT verification
│   └── schemas/
│       ├── __init__.py
│       └── task.py
├── tests/
│   ├── conftest.py
│   ├── test_tasks.py
│   └── test_auth.py
├── requirements.txt
├── .env
└── pyproject.toml
```

## API Contracts

### Authentication

Better Auth handles `/api/auth/*` endpoints. Backend verifies JWT tokens using shared `BETTER_AUTH_SECRET`.

### Task Endpoints

```
GET    /api/tasks          # List user's tasks
POST   /api/tasks          # Create task
PATCH  /api/tasks/{id}     # Update task (title, completed)
DELETE /api/tasks/{id}     # Delete task
```

**Headers**: `Authorization: Bearer <jwt_token>`

**Request/Response Schemas**:

```python
# Create Task
POST /api/tasks
Request:  {"title": "string"}
Response: {"id": "uuid", "title": "string", "completed": false, "created_at": "datetime"}

# Update Task
PATCH /api/tasks/{id}
Request:  {"title": "string"?, "completed": bool?}
Response: {"id": "uuid", "title": "string", "completed": bool, "updated_at": "datetime"}

# List Tasks
GET /api/tasks
Response: [{"id": "uuid", "title": "string", "completed": bool, "created_at": "datetime"}]

# Delete Task
DELETE /api/tasks/{id}
Response: 204 No Content
```

**Error Responses**:
- 401 Unauthorized: Missing or invalid JWT
- 403 Forbidden: Task belongs to different user
- 404 Not Found: Task does not exist
- 422 Validation Error: Invalid request body

## Security Implementation

### JWT Verification (Backend)

```python
# dependencies/auth.py
from jose import jwt
import os

BETTER_AUTH_SECRET = os.environ["BETTER_AUTH_SECRET"]

def get_current_user(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "")
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
    return payload["sub"]  # user_id
```

### User Ownership Enforcement

Every task query includes `WHERE user_id = current_user_id`. No task operation succeeds without this filter.

## Environment Variables

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<shared-secret>
```

### Backend (.env)

```
DATABASE_URL=postgresql://user:pass@neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=<shared-secret>
```

## Complexity Tracking

No constitution violations. Architecture is minimal:
- 2 projects (frontend, backend) - justified by different runtimes
- Direct database access via SQLModel - no repository pattern needed
- Simple JWT verification - no OAuth complexity
