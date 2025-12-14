# Phase II Architecture Plan

**Phase:** phase2-web
**Features:** task-crud, authentication
**Status:** Planning

## Overview

Phase II transforms the Todo app into a full web application with:
- Monorepo structure with shared tooling
- JWT-based authentication (Better Auth + FastAPI verification)
- Database migrations for Neon PostgreSQL
- Docker Compose development environment

---

## 1. Monorepo Setup

### Structure

```
todo_p1/
├── package.json              # Root: workspace scripts
├── docker-compose.yml        # Dev environment orchestration
├── .env.example              # Template for secrets
│
├── frontend/                 # Next.js 14 (App Router)
│   ├── package.json
│   ├── Dockerfile
│   ├── .env.local           # Frontend secrets
│   ├── src/
│   │   ├── app/             # Pages (login, register, dashboard)
│   │   ├── components/      # TaskForm, TaskList, TaskItem
│   │   ├── lib/
│   │   │   ├── auth.ts      # Better Auth config
│   │   │   └── api.ts       # API client with JWT
│   │   └── types/
│   └── CLAUDE.md
│
├── backend/                  # FastAPI
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env                 # Backend secrets
│   ├── app/
│   │   ├── main.py          # App entry, CORS
│   │   ├── config.py        # Settings loader
│   │   ├── database.py      # SQLModel engine
│   │   ├── models/          # User, Task
│   │   ├── schemas/         # Pydantic DTOs
│   │   ├── routers/         # /api/tasks
│   │   └── dependencies/    # auth.py (JWT verify)
│   ├── tests/
│   └── CLAUDE.md
│
├── specs/                    # Specifications
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/
│   │   └── rest-endpoints.md
│   └── database/
│       └── schema.md
│
└── .spec-kit/
    └── config.yaml           # Phase definitions
```

### Root package.json Scripts

```json
{
  "scripts": {
    "dev": "npm run dev:frontend",
    "dev:frontend": "npm --prefix frontend run dev",
    "dev:backend": "cd backend && uvicorn app.main:app --reload",
    "dev:all": "concurrently \"npm run dev:frontend\" \"npm run dev:backend\"",
    "docker:up": "docker-compose up",
    "docker:down": "docker-compose down",
    "docker:build": "docker-compose build",
    "test": "npm run test:backend",
    "test:backend": "cd backend && pytest"
  }
}
```

---

## 2. Authentication Flow with JWT

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │  /login      │    │  /register   │    │  /dashboard  │     │
│   │  Page        │    │  Page        │    │  Page        │     │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│          │                   │                   │              │
│          ▼                   ▼                   ▼              │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              Better Auth Client                      │      │
│   │   - signIn() / signUp()                             │      │
│   │   - JWT Plugin enabled                              │      │
│   │   - Session stored in httpOnly cookie               │      │
│   └─────────────────────────┬───────────────────────────┘      │
│                             │                                   │
│                             ▼                                   │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              API Client (lib/api.ts)                 │      │
│   │   - getAuthToken() from session                     │      │
│   │   - Attach: Authorization: Bearer <token>           │      │
│   └─────────────────────────┬───────────────────────────┘      │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              │ HTTP + JWT
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────┐      │
│   │           Auth Dependency (dependencies/auth.py)     │      │
│   │   1. Extract token from Authorization header         │      │
│   │   2. Verify JWT signature with BETTER_AUTH_SECRET    │      │
│   │   3. Decode payload, extract 'sub' (user_id)        │      │
│   │   4. Return user_id or raise 401                    │      │
│   └─────────────────────────┬───────────────────────────┘      │
│                             │                                   │
│                             ▼                                   │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              Task Router (routers/tasks.py)          │      │
│   │   - GET /api/tasks      → list where user_id=X      │      │
│   │   - POST /api/tasks     → create with user_id=X     │      │
│   │   - PATCH /api/tasks/id → update if owner           │      │
│   │   - DELETE /api/tasks/id → delete if owner          │      │
│   └─────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Shared Secret Configuration

```bash
# Generate a secure secret (run once)
openssl rand -base64 32

# frontend/.env.local
BETTER_AUTH_SECRET=<generated-secret>
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_URL=http://localhost:3000

# backend/.env
BETTER_AUTH_SECRET=<same-generated-secret>
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### JWT Verification Code

```python
# backend/app/dependencies/auth.py
from fastapi import Header, HTTPException, status
from jose import jwt, JWTError
from app.config import settings

def get_current_user_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization[7:]
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")
```

---

## 3. Database Migration Strategy

### Schema Overview

```
┌─────────────────────────┐
│         users           │  ← Managed by Better Auth
├─────────────────────────┤
│ id (UUID) PK            │
│ email (VARCHAR) UNIQUE  │
│ email_verified (BOOL)   │
│ name (VARCHAR)          │
│ image (TEXT)            │
│ created_at (TIMESTAMP)  │
│ updated_at (TIMESTAMP)  │
└───────────┬─────────────┘
            │
            │ 1:N
            ▼
┌─────────────────────────┐
│         tasks           │  ← Application managed
├─────────────────────────┤
│ id (UUID) PK            │
│ title (VARCHAR 255)     │
│ completed (BOOL)        │
│ user_id (UUID) FK       │──→ users.id ON DELETE CASCADE
│ created_at (TIMESTAMP)  │
│ updated_at (TIMESTAMP)  │
└─────────────────────────┘
```

### Migration Approach

**MVP (Current):** SQLModel `create_all()`
```python
# backend/app/database.py
from sqlmodel import SQLModel, create_engine
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

**Production (Future):** Alembic migrations
```bash
# Future setup
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### Better Auth Tables

Better Auth auto-creates these tables on first run:
- `users` - User accounts
- `sessions` - Active sessions
- `accounts` - OAuth providers (if used)
- `verificationTokens` - Email verification

**Important:** Do not manually modify Better Auth tables.

---

## 4. Docker Compose Dev Setup

### docker-compose.yml

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - NEXT_PUBLIC_AUTH_URL=http://localhost:3000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    networks:
      - todo-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    depends_on:
      - db
    volumes:
      - ./backend:/app
    networks:
      - todo-network

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=todo_p1
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - todo-network
    profiles:
      - local-db

networks:
  todo-network:
    driver: bridge

volumes:
  postgres_data:
```

### Dockerfiles

**frontend/Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

**backend/Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Development Commands

```bash
# Start all services (uses Neon DB)
docker-compose up

# Start with local PostgreSQL
docker-compose --profile local-db up

# Rebuild after dependency changes
docker-compose build --no-cache

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Environment Setup

```bash
# Create .env in project root
cp .env.example .env

# Edit with your values
BETTER_AUTH_SECRET=your-secret-here
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/todo_p1?sslmode=require

# For local PostgreSQL development
DATABASE_URL=postgresql://postgres:postgres@db:5432/todo_p1
```

---

## 5. Development Workflow

### Initial Setup

```bash
# 1. Clone and enter project
cd todo_p1

# 2. Setup environment
cp .env.example .env
# Edit .env with secrets

# 3. Install dependencies (local dev)
npm install                    # Root
npm --prefix frontend install  # Frontend
cd backend && pip install -r requirements.txt  # Backend

# 4. Start development
npm run dev:all               # Both services
# OR
docker-compose up             # Via Docker
```

### Daily Development

```bash
# Option A: Local (faster iteration)
npm run dev:frontend          # Terminal 1
npm run dev:backend           # Terminal 2

# Option B: Docker (consistent env)
docker-compose up
```

### Testing

```bash
# Backend tests
cd backend && pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_tasks.py -v
```

---

## 6. Phase II Checklist

### Infrastructure
- [ ] Root package.json with workspace scripts
- [ ] docker-compose.yml with all services
- [ ] Dockerfiles for frontend and backend
- [ ] .env.example template

### Authentication
- [ ] Better Auth configured in frontend
- [ ] JWT plugin enabled
- [ ] Auth pages (login, register)
- [ ] JWT verification in FastAPI
- [ ] Protected route middleware

### Database
- [ ] SQLModel models (User, Task)
- [ ] Database connection with Neon
- [ ] create_all() on startup
- [ ] User-task relationship with FK

### API
- [ ] GET /api/tasks (filtered by user)
- [ ] POST /api/tasks (with user_id)
- [ ] PATCH /api/tasks/{id} (ownership check)
- [ ] DELETE /api/tasks/{id} (ownership check)
- [ ] CORS configured

### Frontend
- [ ] Login page with form
- [ ] Register page with form
- [ ] Dashboard with task list
- [ ] API client with auth header
- [ ] Protected route redirect

### Testing
- [ ] Auth flow tests
- [ ] Task CRUD tests
- [ ] User isolation tests
- [ ] Error handling tests

---

## 7. Security Checklist

- [ ] BETTER_AUTH_SECRET is 32+ characters
- [ ] Secret is identical in both services
- [ ] Secrets loaded from environment only
- [ ] No secrets in code or git
- [ ] CORS restricted to frontend origin
- [ ] user_id always from JWT, never client
- [ ] 403 on ownership violations
- [ ] Input validation on all endpoints
