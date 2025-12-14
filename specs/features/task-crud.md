# Feature: Task CRUD

**Status:** Active
**Phase:** phase2-web
**Priority:** P1

## Overview

Core task management functionality allowing authenticated users to create, read, update, and delete their personal tasks.

## User Stories

### US-1: Create Task
**As a** logged-in user
**I want to** create a new task
**So that** I can track things I need to do

**Acceptance Criteria:**
- [ ] User can enter task title in input field
- [ ] Clicking "Add" or pressing Enter creates the task
- [ ] New task appears immediately in the list
- [ ] Empty titles are rejected with validation error
- [ ] Task is persisted to database with user ownership

### US-2: View Tasks
**As a** logged-in user
**I want to** see all my tasks
**So that** I know what I need to do

**Acceptance Criteria:**
- [ ] Dashboard displays all user's tasks on load
- [ ] Tasks show title and completion status
- [ ] Only the authenticated user's tasks are visible
- [ ] Empty state shown when no tasks exist

### US-3: Complete Task
**As a** logged-in user
**I want to** mark tasks as complete/incomplete
**So that** I can track my progress

**Acceptance Criteria:**
- [ ] Checkbox toggles task completion status
- [ ] Completed tasks have visual distinction (strikethrough)
- [ ] Status change persists immediately
- [ ] Optimistic UI update with rollback on error

### US-4: Edit Task
**As a** logged-in user
**I want to** edit task titles
**So that** I can fix mistakes or update details

**Acceptance Criteria:**
- [ ] Click on task enables inline editing
- [ ] Enter or blur saves changes
- [ ] Escape cancels editing
- [ ] Empty title reverts to original

### US-5: Delete Task
**As a** logged-in user
**I want to** delete tasks
**So that** I can remove items I no longer need

**Acceptance Criteria:**
- [ ] Delete button/icon on each task
- [ ] Task removed immediately from UI
- [ ] Deletion persists to database
- [ ] No confirmation required (keep UX simple)

## Security Requirements

- All operations require valid JWT token
- User can only access their own tasks (user_id from token, not client)
- Backend enforces ownership on every operation
- 403 returned if user tries to access another user's task

## API Dependencies

See `@specs/api/rest-endpoints.md` for endpoint details.

## UI Components

| Component | Location | Purpose |
|-----------|----------|---------|
| TaskForm | `src/components/TaskForm.tsx` | Create new tasks |
| TaskList | `src/components/TaskList.tsx` | Display task list |
| TaskItem | `src/components/TaskItem.tsx` | Individual task with actions |

## Test Scenarios

1. **Create:** Submit form → task appears in list
2. **Read:** Page load → all user tasks displayed
3. **Update:** Toggle checkbox → status persists after refresh
4. **Delete:** Click delete → task removed from list
5. **Isolation:** User A cannot see/modify User B's tasks
