# Tasks: Todo App

**Input**: Design documents from `/specs/todo-app/`
**Prerequisites**: plan.md (required), spec.md (required)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project root structure with frontend/ and backend/ directories
- [ ] T002 [P] Initialize Next.js project with TypeScript in frontend/
- [ ] T003 [P] Initialize Python project with FastAPI in backend/
- [ ] T004 Configure Tailwind CSS in frontend/
- [ ] T005 [P] Create .env.example files for both frontend and backend
- [ ] T006 [P] Configure ESLint and Prettier for frontend
- [ ] T007 [P] Configure Python linting (ruff) for backend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

- [ ] T008 Setup SQLModel database connection with Neon PostgreSQL in backend/app/database.py
- [ ] T009 Create User model in backend/app/models/user.py
- [ ] T010 Create Task model in backend/app/models/task.py (depends on T009)
- [ ] T011 Implement JWT verification dependency in backend/app/dependencies/auth.py
- [ ] T012 Setup Better Auth client in frontend/src/lib/auth.ts
- [ ] T013 Create API client utility in frontend/src/lib/api.ts
- [ ] T014 Create shared TypeScript types in frontend/src/types/index.ts

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Authentication (Priority: P1)

**Goal**: Users can register, login, and logout

### Tests for US1

- [ ] T015 [US1] Write backend test for JWT verification in backend/tests/test_auth.py
- [ ] T016 [US1] Write frontend test for auth flow in frontend/__tests__/auth.test.tsx

### Implementation for US1

- [ ] T017 [US1] Create root layout with auth provider in frontend/src/app/layout.tsx
- [ ] T018 [P] [US1] Create login page in frontend/src/app/login/page.tsx
- [ ] T019 [P] [US1] Create register page in frontend/src/app/register/page.tsx
- [ ] T020 [US1] Create dashboard layout with auth guard in frontend/src/app/dashboard/layout.tsx
- [ ] T021 [US1] Add logout functionality to dashboard

**Checkpoint**: Users can register, login, logout - proceed to US2

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P1)

**Goal**: Users can create tasks and see their task list

### Tests for US2

- [ ] T022 [US2] Write backend tests for GET /api/tasks in backend/tests/test_tasks.py
- [ ] T023 [US2] Write backend tests for POST /api/tasks in backend/tests/test_tasks.py
- [ ] T024 [US2] Write test for user ownership enforcement (User A can't see User B's tasks)

### Implementation for US2

- [ ] T025 [US2] Create task schemas in backend/app/schemas/task.py
- [ ] T026 [US2] Implement GET /api/tasks endpoint in backend/app/routers/tasks.py
- [ ] T027 [US2] Implement POST /api/tasks endpoint in backend/app/routers/tasks.py
- [ ] T028 [US2] Register tasks router in backend/app/main.py
- [ ] T029 [P] [US2] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [ ] T030 [P] [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [ ] T031 [US2] Create TaskList component in frontend/src/components/TaskList.tsx
- [ ] T032 [US2] Implement dashboard page with task list in frontend/src/app/dashboard/page.tsx

**Checkpoint**: Users can create and view their tasks - proceed to US3

---

## Phase 5: User Story 3 - Complete and Delete Tasks (Priority: P2)

**Goal**: Users can mark tasks complete and delete them

### Tests for US3

- [ ] T033 [US3] Write backend tests for PATCH /api/tasks/{id} in backend/tests/test_tasks.py
- [ ] T034 [US3] Write backend tests for DELETE /api/tasks/{id} in backend/tests/test_tasks.py
- [ ] T035 [US3] Write test for ownership enforcement on PATCH/DELETE (403 for other user's tasks)

### Implementation for US3

- [ ] T036 [US3] Implement PATCH /api/tasks/{id} endpoint in backend/app/routers/tasks.py
- [ ] T037 [US3] Implement DELETE /api/tasks/{id} endpoint in backend/app/routers/tasks.py
- [ ] T038 [US3] Add toggle complete handler to TaskItem component
- [ ] T039 [US3] Add delete handler to TaskItem component
- [ ] T040 [US3] Add visual styling for completed tasks (strikethrough, opacity)

**Checkpoint**: Core todo functionality complete - proceed to US4

---

## Phase 6: User Story 4 - Edit Tasks (Priority: P3)

**Goal**: Users can edit task titles

### Tests for US4

- [ ] T041 [US4] Write backend test for title update via PATCH in backend/tests/test_tasks.py
- [ ] T042 [US4] Write test for ownership enforcement on edit

### Implementation for US4

- [ ] T043 [US4] Add inline edit mode to TaskItem component
- [ ] T044 [US4] Implement edit save/cancel functionality
- [ ] T045 [US4] Add keyboard shortcuts (Enter to save, Escape to cancel)

**Checkpoint**: All user stories complete

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: Final refinements

- [ ] T046 [P] Add loading states to all async operations
- [ ] T047 [P] Add error handling and user-friendly error messages
- [ ] T048 [P] Add empty state for task list ("No tasks yet")
- [ ] T049 Responsive styling for mobile devices
- [ ] T050 Create .env.example with all required variables documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-6 (User Stories)**: Depend on Phase 2, can proceed sequentially P1→P2→P3
- **Phase 7 (Polish)**: Depends on all user stories

### Parallel Opportunities

```
Phase 1:
  T002, T003 can run in parallel (different directories)
  T005, T006, T007 can run in parallel

Phase 2:
  After T008: T009, T010 can run in parallel
  T012, T013, T014 can run in parallel (frontend)

Phase 4:
  T029, T030 can run in parallel (different components)

Phase 7:
  T046, T047, T048 can run in parallel
```

---

## Notes

- All backend endpoints MUST include user ownership check
- All frontend API calls MUST include Authorization header
- Tests MUST verify 403 responses for cross-user access attempts
- No hardcoded secrets - verify .env usage before each phase completion
