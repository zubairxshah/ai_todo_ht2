# Feature Specification: Todo App

**Feature Branch**: `001-todo-app`
**Created**: 2025-12-14
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - User Registration & Login (Priority: P1)

As a user, I want to register and log in so that my tasks are private and persistent.

**Why this priority**: Authentication is foundational; no other features work without it.

**Independent Test**: Can register, log in, and see an empty task list.

**Acceptance Scenarios**:

1. **Given** I am a new user, **When** I register with email/password, **Then** I am logged in and see the task dashboard
2. **Given** I am a registered user, **When** I log in with correct credentials, **Then** I am redirected to my task dashboard
3. **Given** I am logged in, **When** I click logout, **Then** I am redirected to the login page and my session is cleared
4. **Given** I enter incorrect credentials, **When** I try to log in, **Then** I see an error message and remain on login page

---

### User Story 2 - Create and View Tasks (Priority: P1)

As a user, I want to create tasks and see them in a list so I can track what I need to do.

**Why this priority**: Core functionality - a todo app must allow creating and viewing tasks.

**Independent Test**: Can create a task and see it appear in the list immediately.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I enter a task title and click "Add", **Then** the task appears in my task list
2. **Given** I have tasks, **When** I view my dashboard, **Then** I see all my tasks listed
3. **Given** I am logged in as User A, **When** I view tasks, **Then** I only see tasks I created (not User B's tasks)

---

### User Story 3 - Complete and Delete Tasks (Priority: P2)

As a user, I want to mark tasks as complete and delete them so I can manage my task list.

**Why this priority**: Essential task management after creation.

**Independent Test**: Can toggle task completion and delete tasks.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task, **When** I click the checkbox, **Then** the task is marked as complete with visual indication
2. **Given** I have a complete task, **When** I click the checkbox, **Then** the task is marked as incomplete
3. **Given** I have a task, **When** I click delete, **Then** the task is removed from my list
4. **Given** I am User A, **When** I try to complete/delete User B's task, **Then** the operation is denied (403)

---

### User Story 4 - Edit Tasks (Priority: P3)

As a user, I want to edit task titles so I can correct or update them.

**Why this priority**: Nice-to-have refinement after core CRUD.

**Independent Test**: Can edit a task title and see the change persist.

**Acceptance Scenarios**:

1. **Given** I have a task, **When** I click edit and change the title, **Then** the new title is saved and displayed
2. **Given** I am User A, **When** I try to edit User B's task, **Then** the operation is denied (403)

---

### Edge Cases

- What happens when a user tries to create an empty task? → Validation error, task not created
- What happens when JWT expires? → User is redirected to login
- What happens when database is unavailable? → Graceful error message displayed
- What happens when a user tries to access tasks without authentication? → Redirect to login

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow user registration with email and password
- **FR-002**: System MUST authenticate users via Better Auth with JWT plugin
- **FR-003**: System MUST share BETTER_AUTH_SECRET between frontend and backend for JWT verification
- **FR-004**: System MUST enforce user ownership on all task CRUD operations
- **FR-005**: System MUST store tasks in Neon PostgreSQL via SQLModel
- **FR-006**: System MUST provide REST API endpoints for task operations
- **FR-007**: Frontend MUST use Next.js App Router for navigation
- **FR-008**: Frontend MUST use Tailwind CSS for styling
- **FR-009**: All secrets MUST be loaded from environment variables

### Key Entities

- **User**: id (UUID), email (unique), password_hash, created_at
- **Task**: id (UUID), title (string), completed (boolean), user_id (FK to User), created_at, updated_at

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete registration and login flow in under 30 seconds
- **SC-002**: Task CRUD operations complete in under 200ms (p95)
- **SC-003**: User A cannot access User B's tasks under any circumstance
- **SC-004**: No secrets exposed in client-side code or responses
