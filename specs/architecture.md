# Todo P1 - Architecture

## System Architecture (Phase I-II)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Next.js App   │────▶│   FastAPI       │────▶│   Neon         │
│   (Frontend)    │     │   (Backend)     │     │   PostgreSQL   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     Port 3000              Port 8000              Cloud DB

         │                      │
         │                      │
         ▼                      ▼
    Better Auth            JWT Verify
    (Session Mgmt)         (PyJWT + JWKS)
         │                      │
         └──────────────────────┘
                    │
                    ▼
            EdDSA Keys (JWKS)
```

## Phase III Architecture (AI Chatbot + MCP)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────────┐  │
│  │  Task UI    │  │  Auth UI    │  │         Chat Interface              │  │
│  │  (CRUD)     │  │  (Login)    │  │   ┌─────────────────────────────┐   │  │
│  └──────┬──────┘  └──────┬──────┘  │   │   OpenAI ChatKit Component  │   │  │
│         │                │         │   └─────────────┬───────────────┘   │  │
│         └────────────────┴─────────┴─────────────────┼───────────────────┘  │
│                                                      │                       │
└──────────────────────────────────────────────────────┼───────────────────────┘
                           │                           │
                           │ REST API                  │ POST /api/chat
                           ▼                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  /api/tasks     │  │  Auth Middleware │  │      /api/chat             │  │
│  │  (CRUD Router)  │  │  (JWT Verify)    │  │  ┌─────────────────────┐   │  │
│  └────────┬────────┘  └────────┬─────────┘  │  │  OpenAI Agents SDK  │   │  │
│           │                    │            │  │  (Agent Runner)     │   │  │
│           │                    │            │  └──────────┬──────────┘   │  │
│           │                    │            │             │              │  │
│           │                    │            │  ┌──────────▼──────────┐   │  │
│           │                    │            │  │     MCP Server      │   │  │
│           │                    │            │  │  ┌───────────────┐  │   │  │
│           │                    │            │  │  │  add_task     │  │   │  │
│           │                    │            │  │  │  list_tasks   │  │   │  │
│           │                    │            │  │  │  complete_task│  │   │  │
│           │                    │            │  │  │  update_task  │  │   │  │
│           │                    │            │  │  │  delete_task  │  │   │  │
│           │                    │            │  │  └───────────────┘  │   │  │
│           │                    │            │  └──────────┬──────────┘   │  │
│           └────────────────────┴────────────┴────────────┼───────────────┘  │
│                                                          │                   │
└──────────────────────────────────────────────────────────┼───────────────────┘
                                                           │
                                                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE (Neon PostgreSQL)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │     users       │  │     tasks       │  │  conversations / messages   │  │
│  │  (Better Auth)  │  │   (user_id FK)  │  │      (user_id scoped)       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Chat Request Flow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  User   │    │ ChatKit │    │ FastAPI │    │  Agent  │    │   MCP   │
│ Browser │    │   UI    │    │ /chat   │    │ Runner  │    │  Tools  │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │              │
     │ "Add milk"   │              │              │              │
     │─────────────▶│              │              │              │
     │              │ POST /chat   │              │              │
     │              │─────────────▶│              │              │
     │              │              │ Verify JWT   │              │
     │              │              │─────────────▶│              │
     │              │              │              │              │
     │              │              │ Run Agent    │              │
     │              │              │─────────────▶│              │
     │              │              │              │ call add_task│
     │              │              │              │─────────────▶│
     │              │              │              │              │
     │              │              │              │    result    │
     │              │              │              │◀─────────────│
     │              │              │              │              │
     │              │              │   response   │              │
     │              │◀─────────────│◀─────────────│              │
     │  "✅ Added"  │              │              │              │
     │◀─────────────│              │              │              │
     │              │              │              │              │
```

## Component Overview

### Frontend (Next.js)

**Location**: `frontend/`

**Responsibilities**:
- User interface rendering
- Client-side routing (App Router)
- Authentication UI (login, register, logout)
- Task management UI (CRUD operations)
- API communication with backend

**Key Directories**:
- `src/app/` - Next.js pages and routes
- `src/components/` - Reusable React components
- `src/lib/` - Utilities and API client
- `src/types/` - TypeScript type definitions

### Backend (FastAPI)

**Location**: `backend/`

**Responsibilities**:
- REST API endpoints
- JWT token verification
- Database operations via SQLModel
- User ownership enforcement
- Business logic

**Key Directories**:
- `app/routers/` - API route handlers
- `app/models/` - SQLModel database models
- `app/schemas/` - Pydantic request/response schemas
- `app/dependencies/` - Dependency injection (auth)
- `tests/` - Pytest test suite

## Data Flow

### Authentication Flow

```
1. User submits credentials (login/register)
2. Better Auth (frontend) creates session + JWT
3. JWT stored in cookie/header
4. Frontend sends JWT with API requests
5. Backend verifies JWT using shared secret
6. Backend extracts user_id from JWT claims
7. Backend uses user_id for data filtering
```

### Task CRUD Flow

```
1. Frontend sends request with Authorization header
2. Backend auth dependency extracts + verifies JWT
3. Backend extracts user_id from verified token
4. Database query filtered by user_id
5. Response returned to frontend
6. Frontend updates UI state
```

## Database Schema

### Users Table (managed by Better Auth)

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| email | VARCHAR | UNIQUE, NOT NULL |
| password_hash | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

### Tasks Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| title | VARCHAR(255) | NOT NULL |
| completed | BOOLEAN | DEFAULT FALSE |
| user_id | UUID | FK → users.id, NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### Conversation Table (Phase III)

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | VARCHAR | NOT NULL, INDEX |
| title | VARCHAR(255) | NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### Message Table (Phase III)

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| conversation_id | UUID | FK → conversation.id |
| role | VARCHAR(20) | NOT NULL |
| content | TEXT | NOT NULL |
| tool_calls | JSONB | NULL |
| metadata | JSONB | NULL |
| created_at | TIMESTAMP | NOT NULL |

## API Design

### Endpoints (Phase I-II)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /health | Health check | No |
| GET | /api/tasks | List user's tasks | Yes |
| POST | /api/tasks | Create task | Yes |
| PATCH | /api/tasks/{id} | Update task | Yes |
| DELETE | /api/tasks/{id} | Delete task | Yes |

### Endpoints (Phase III - Chat)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/chat | Send message to AI | Yes |
| GET | /api/chat/history | Get conversation history | Yes |
| DELETE | /api/chat/history | Clear conversation history | Yes |

### Authentication Header

```
Authorization: Bearer <jwt_token>
```

## Security Measures

1. **JWT Verification**: All protected endpoints verify JWT signature
2. **User Isolation**: Queries always filtered by authenticated user_id
3. **Environment Variables**: All secrets loaded from `.env` files
4. **CORS**: Restricted to frontend origin only
5. **Input Validation**: Pydantic schemas validate all inputs

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| API Response Time (p95) | < 200ms |
| Authentication Flow | < 30s |
| Availability | 99.9% |
| Data Isolation | 100% (user A cannot access user B's data) |

## Technology Decisions

### Why Next.js?
- Server-side rendering for performance
- App Router for modern routing patterns
- Built-in API routes if needed
- TypeScript support out of the box

### Why FastAPI?
- High performance async framework
- Automatic OpenAPI documentation
- Pydantic for data validation
- SQLModel integration for ORM

### Why Neon PostgreSQL?
- Serverless PostgreSQL
- Auto-scaling
- Built-in connection pooling
- Cost-effective for small projects

### Why Better Auth?
- Modern auth solution
- JWT plugin for stateless auth (EdDSA)
- Easy integration with Next.js
- Session management built-in

### Why OpenAI Agents SDK? (Phase III)
- Native tool calling support
- Streaming responses
- Context management
- Easy integration with MCP

### Why MCP (Model Context Protocol)? (Phase III)
- Standardized tool interface
- Clean separation of concerns
- Reusable across different LLM providers
- User-scoped tool execution

## Phase III Components

### MCP Server

The MCP server exposes task management tools to the AI agent:

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task |
| `list_tasks` | List tasks with optional filters |
| `complete_task` | Mark a task as completed |
| `update_task` | Update a task's title |
| `delete_task` | Delete a task |

All tools automatically receive `user_id` from the authenticated session to ensure data isolation.

### Agent Configuration

```python
SYSTEM_PROMPT = """
You are a helpful todo assistant. You help users manage their tasks through natural conversation.
You have access to tools that let you add, list, complete, update, and delete tasks.
Always confirm actions you take and provide clear summaries.
Be concise but friendly.
"""
```

See [@specs/features/chatbot.md](./features/chatbot.md) for full agent behavior specification.
