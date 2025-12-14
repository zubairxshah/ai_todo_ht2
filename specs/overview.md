# Todo P1 - Project Overview

## Purpose

A full-stack Todo application that allows users to manage their personal tasks with secure authentication and data isolation.

## Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend Framework | Next.js (App Router) | 14.x |
| Frontend Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.4.x |
| Authentication | Better Auth | 1.x |
| Backend Framework | FastAPI | 0.109+ |
| ORM | SQLModel | 0.0.14+ |
| Database | Neon PostgreSQL | - |
| Auth Verification | JWT (python-jose) | 3.3+ |

## Core Features

1. **User Authentication**
   - Registration with email/password
   - Login/logout functionality
   - JWT-based session management
   - Shared secret between frontend and backend

2. **Task Management**
   - Create new tasks
   - View personal task list
   - Mark tasks as complete/incomplete
   - Edit task titles (inline editing)
   - Delete tasks

3. **Security**
   - User data isolation (users only see their own tasks)
   - All secrets loaded from environment variables
   - CORS configured for frontend origin only

## Project Structure

```
todo_p1/
├── frontend/           # Next.js application
├── backend/            # FastAPI application
├── specs/              # Specifications and documentation
│   ├── features/       # Feature specifications
│   ├── api/            # API documentation
│   ├── database/       # Database schemas
│   ├── ui/             # UI/UX specifications
│   └── todo-app/       # Main feature spec
├── history/            # Prompt history records
└── .spec-kit/          # SpecKit configuration
```

## Getting Started

See [README.md](../README.md) for setup instructions.

## Related Documents

- [Architecture](./architecture.md) - System architecture and design decisions
- [Feature Spec](./todo-app/spec.md) - Detailed feature specifications
- [Implementation Plan](./todo-app/plan.md) - Implementation approach
- [Tasks](./todo-app/tasks.md) - Development tasks
