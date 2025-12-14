---
id: 001
title: Todo App Full Implementation
stage: spec
date: 2025-12-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-app
branch: 001-todo-app
user: codeworks
command: /sp.constitution + implementation
labels: ["nextjs", "fastapi", "todo", "full-stack", "better-auth"]
links:
  spec: specs/todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - specs/todo-app/spec.md
  - specs/todo-app/plan.md
  - specs/todo-app/tasks.md
  - frontend/src/app/layout.tsx
  - frontend/src/app/page.tsx
  - frontend/src/app/login/page.tsx
  - frontend/src/app/register/page.tsx
  - frontend/src/app/dashboard/page.tsx
  - frontend/src/components/TaskForm.tsx
  - frontend/src/components/TaskList.tsx
  - frontend/src/components/TaskItem.tsx
  - frontend/src/lib/auth.ts
  - frontend/src/lib/api.ts
  - frontend/src/types/index.ts
  - backend/app/main.py
  - backend/app/config.py
  - backend/app/database.py
  - backend/app/models/user.py
  - backend/app/models/task.py
  - backend/app/routers/tasks.py
  - backend/app/dependencies/auth.py
  - backend/app/schemas/task.py
  - backend/tests/conftest.py
  - backend/tests/test_tasks.py
  - backend/tests/test_auth.py
  - README.md
tests:
  - backend/tests/test_tasks.py
  - backend/tests/test_auth.py
---

## Prompt

create a todo app on nextjs framework including following features nextjs router, use tailwind css, backend: FastAPI + SQLModel + Neon PostGres, Auth: better Auth with JWT plugin, shared BETTER_AUTH_SECRET, enforce user ownership on all task operations, use environment variables for secrets

## Response snapshot

Created a full-stack Todo application with:
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Better Auth client
- **Backend**: FastAPI, SQLModel, Neon PostgreSQL, JWT auth
- **Features**: User registration/login, CRUD tasks, user ownership enforcement
- **Security**: Shared BETTER_AUTH_SECRET, environment variables, 403 for cross-user access

Project structure created with:
- Constitution defining 4 core principles (TDD, Simplicity, Security-First, Type Safety)
- Feature specification with 4 user stories
- Implementation plan with technical context
- 50 tasks organized by user story priority
- Full implementation of frontend and backend
- Comprehensive test suite for auth and tasks

## Outcome

- ✅ Impact: Full-stack todo app scaffolded and implemented
- 🧪 Tests: 13 backend tests covering auth and task CRUD with ownership
- 📁 Files: 25+ files created across frontend, backend, and specs
- 🔁 Next prompts: Run npm install, pip install, configure .env files, test the app
- 🧠 Reflection: Spec-driven approach ensured comprehensive coverage of requirements

## Evaluation notes (flywheel)

- Failure modes observed: npx create-next-app failed on WSL UNC path, worked around by manual setup
- Graders run and results (PASS/FAIL): N/A - implementation phase
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add E2E tests with Playwright
