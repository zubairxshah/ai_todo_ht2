# Phase V: Advanced Features Specification

## Overview

This spec defines all advanced and intermediate features to be added in Phase V.

## Feature Summary

| Feature | Priority | Complexity | Dependencies |
|---------|----------|------------|--------------|
| Due Dates | P0 | Low | DB schema |
| Priorities | P0 | Low | DB schema |
| Tags | P1 | Medium | DB schema, junction table |
| Reminders | P1 | Medium | Due dates, Kafka, Notification Service |
| Recurring Tasks | P1 | High | Kafka, Recurring Task Service |
| Search | P2 | Medium | Full-text index |
| Filter | P2 | Low | API query params |
| Sort | P2 | Low | API query params |

---

## 1. Due Dates

### Description
Allow users to set a deadline for tasks.

### Database Changes
```sql
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE NULL;
```

### API Changes

**Create Task**
```json
POST /api/tasks
{
  "title": "Buy groceries",
  "due_date": "2025-12-20T18:00:00Z"  // Optional
}
```

**Update Task**
```json
PATCH /api/tasks/{id}
{
  "due_date": "2025-12-21T18:00:00Z"
}
```

**Response**
```json
{
  "id": "uuid",
  "title": "Buy groceries",
  "completed": false,
  "due_date": "2025-12-20T18:00:00Z",
  "created_at": "2025-12-15T10:00:00Z",
  "updated_at": "2025-12-15T10:00:00Z"
}
```

### MCP Tool Updates
```python
@mcp.tool()
def add_task(title: str, user_id: str, due_date: str | None = None) -> dict:
    """Create a new task with optional due date."""
    # due_date format: ISO 8601 (e.g., "2025-12-20T18:00:00Z")
```

### Chat Examples
```
User: "Add buy groceries due Friday"
AI: Created task "buy groceries" due Dec 20, 2025.

User: "Set due date for groceries to tomorrow at 5pm"
AI: Updated "buy groceries" - due Dec 16, 2025 at 5:00 PM.
```

---

## 2. Priorities

### Description
Assign priority levels to tasks for better organization.

### Priority Levels
| Value | Label | Display |
|-------|-------|---------|
| 1 | High | 🔴 |
| 2 | Medium | 🟡 |
| 3 | Low | 🟢 |
| NULL | None | - |

### Database Changes
```sql
ALTER TABLE tasks ADD COLUMN priority INTEGER CHECK (priority IN (1, 2, 3));
```

### API Changes

**Create/Update Task**
```json
{
  "title": "Buy groceries",
  "priority": 1  // 1=High, 2=Medium, 3=Low, null=None
}
```

### MCP Tool Updates
```python
@mcp.tool()
def add_task(
    title: str,
    user_id: str,
    due_date: str | None = None,
    priority: int | None = None  # 1=High, 2=Medium, 3=Low
) -> dict:
    """Create a new task with optional priority."""
```

### Chat Examples
```
User: "Add urgent meeting prep with high priority"
AI: Created task "meeting prep" with HIGH priority.

User: "Set groceries to low priority"
AI: Updated "buy groceries" to LOW priority.

User: "Show my high priority tasks"
AI: High priority tasks:
    1. [🔴] Meeting prep (due today)
    2. [🔴] Call client
```

---

## 3. Tags

### Description
Categorize tasks with multiple labels/tags.

### Database Changes

**Tags Table**
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',  -- Hex color
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, user_id)
);
```

**Task-Tags Junction Table**
```sql
CREATE TABLE task_tags (
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
```

### API Endpoints

**Tags CRUD**
```
GET    /api/tags              - List user's tags
POST   /api/tags              - Create tag {"name": "work", "color": "#EF4444"}
DELETE /api/tags/{id}         - Delete tag
```

**Task with Tags**
```json
POST /api/tasks
{
  "title": "Review PR",
  "tags": ["work", "urgent"]  // Tag names, auto-create if not exist
}
```

**Response**
```json
{
  "id": "uuid",
  "title": "Review PR",
  "tags": [
    {"id": "uuid", "name": "work", "color": "#EF4444"},
    {"id": "uuid", "name": "urgent", "color": "#F59E0B"}
  ]
}
```

### MCP Tool Updates
```python
@mcp.tool()
def add_task(
    title: str,
    user_id: str,
    tags: list[str] | None = None
) -> dict:
    """Create task with optional tags."""

@mcp.tool()
def list_tasks(
    user_id: str,
    tag: str | None = None  # Filter by tag name
) -> dict:
    """List tasks, optionally filtered by tag."""
```

### Chat Examples
```
User: "Add review PR tagged work and urgent"
AI: Created "review PR" with tags: #work, #urgent

User: "Show my work tasks"
AI: Tasks tagged #work:
    1. [ ] Review PR
    2. [x] Send report
```

---

## 4. Reminders

### Description
Schedule notifications before task due dates.

### Database Changes
```sql
ALTER TABLE tasks ADD COLUMN remind_at TIMESTAMP WITH TIME ZONE NULL;
```

### Reminder Logic
- Default: 1 hour before due date
- Custom: User specifies exact time
- Stored as `remind_at` timestamp

### Kafka Event (Published when reminder set)
```json
{
  "topic": "reminders",
  "event_type": "reminder.scheduled",
  "task_id": "uuid",
  "title": "Buy groceries",
  "due_at": "2025-12-20T18:00:00Z",
  "remind_at": "2025-12-20T17:00:00Z",
  "user_id": "user-123"
}
```

### Dapr Jobs API Integration
```python
async def schedule_reminder(task_id: str, remind_at: datetime, user_id: str):
    """Schedule reminder using Dapr Jobs API."""
    await httpx.post(
        f"http://localhost:3500/v1.0-alpha1/jobs/reminder-{task_id}",
        json={
            "dueTime": remind_at.isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "type": "reminder"
            }
        }
    )
```

### MCP Tool Updates
```python
@mcp.tool()
def add_task(
    title: str,
    user_id: str,
    due_date: str | None = None,
    remind_before_minutes: int = 60  # Default 1 hour
) -> dict:
    """Create task with reminder (default: 1 hour before due)."""
```

### Chat Examples
```
User: "Add dentist appointment Friday 3pm, remind me 2 hours before"
AI: Created "dentist appointment" due Dec 20 at 3:00 PM.
    Reminder set for 1:00 PM.

User: "Remind me about groceries tomorrow morning"
AI: Set reminder for "buy groceries" at Dec 16, 9:00 AM.
```

---

## 5. Recurring Tasks

### Description
Tasks that automatically recreate when completed.

### Recurrence Patterns
| Pattern | RRULE | Example |
|---------|-------|---------|
| Daily | `FREQ=DAILY` | Every day |
| Weekly | `FREQ=WEEKLY;BYDAY=MO,WE,FR` | Mon, Wed, Fri |
| Monthly | `FREQ=MONTHLY;BYMONTHDAY=1` | 1st of month |
| Custom | Full RRULE string | Any pattern |

### Database Changes
```sql
ALTER TABLE tasks ADD COLUMN recurrence_rule VARCHAR(255) NULL;
ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE tasks ADD COLUMN parent_task_id UUID REFERENCES tasks(id) NULL;
```

### Kafka Event (Published when recurring task completed)
```json
{
  "topic": "task-events",
  "event_type": "task.completed",
  "task_id": "uuid",
  "title": "Daily standup",
  "recurrence_rule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
  "user_id": "user-123"
}
```

### Recurring Task Service (Consumer)
```python
async def handle_task_completed(event: dict):
    """Create next occurrence when recurring task completed."""
    if event.get("recurrence_rule"):
        next_due = calculate_next_occurrence(
            event["recurrence_rule"],
            event.get("due_date")
        )
        if next_due and (not event.get("recurrence_end_date") or next_due < event["recurrence_end_date"]):
            await create_task(
                title=event["title"],
                user_id=event["user_id"],
                due_date=next_due,
                recurrence_rule=event["recurrence_rule"],
                parent_task_id=event["task_id"]
            )
```

### MCP Tool Updates
```python
@mcp.tool()
def add_task(
    title: str,
    user_id: str,
    recurrence: str | None = None  # "daily", "weekly", "monthly", or RRULE
) -> dict:
    """Create task with optional recurrence."""
```

### Chat Examples
```
User: "Add daily standup every weekday at 9am"
AI: Created recurring task "daily standup" at 9:00 AM weekdays.

User: "Add pay rent on the 1st of every month"
AI: Created recurring task "pay rent" on the 1st of each month.

User: "Complete the standup task"
AI: Completed "daily standup". Next occurrence: Dec 17 at 9:00 AM.
```

---

## 6. Search

### Description
Full-text search across task titles.

### Database Changes
```sql
-- Add full-text search index
CREATE INDEX tasks_title_search_idx ON tasks USING GIN (to_tsvector('english', title));
```

### API Endpoint
```
GET /api/tasks?search=groceries
```

### SQL Query
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND to_tsvector('english', title) @@ plainto_tsquery('english', $2)
ORDER BY ts_rank(to_tsvector('english', title), plainto_tsquery('english', $2)) DESC;
```

### MCP Tool Updates
```python
@mcp.tool()
def list_tasks(
    user_id: str,
    search: str | None = None
) -> dict:
    """List tasks with optional search query."""
```

### Chat Examples
```
User: "Search for meeting"
AI: Found 3 tasks matching "meeting":
    1. [ ] Team meeting (due today)
    2. [x] Client meeting
    3. [ ] Meeting prep
```

---

## 7. Filter

### Description
Filter tasks by various criteria.

### Filter Parameters
| Parameter | Type | Example |
|-----------|------|---------|
| `status` | string | `pending`, `completed`, `all` |
| `priority` | int | `1`, `2`, `3` |
| `tag` | string | `work`, `personal` |
| `due_before` | datetime | `2025-12-20T00:00:00Z` |
| `due_after` | datetime | `2025-12-15T00:00:00Z` |
| `overdue` | boolean | `true` |

### API Endpoint
```
GET /api/tasks?status=pending&priority=1&tag=work&overdue=true
```

### MCP Tool Updates
```python
@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",  # "pending", "completed", "all"
    priority: int | None = None,
    tag: str | None = None,
    overdue: bool = False
) -> dict:
    """List tasks with filters."""
```

### Chat Examples
```
User: "Show overdue tasks"
AI: Overdue tasks:
    1. [🔴] Pay bills (due Dec 10)
    2. [🟡] Call mom (due Dec 14)

User: "Show high priority pending tasks"
AI: High priority pending:
    1. [ ] Meeting prep (due today)
```

---

## 8. Sort

### Description
Sort tasks by different fields.

### Sort Options
| Parameter | Values |
|-----------|--------|
| `sort_by` | `due_date`, `priority`, `created_at`, `title` |
| `sort_order` | `asc`, `desc` |

### API Endpoint
```
GET /api/tasks?sort_by=due_date&sort_order=asc
```

### Default Sort
- Pending tasks: `due_date ASC` (soonest first)
- Completed tasks: `updated_at DESC` (recently completed first)

### Chat Examples
```
User: "Show tasks by priority"
AI: Tasks by priority:
    🔴 HIGH:
    1. Meeting prep
    2. Call client
    🟡 MEDIUM:
    3. Review PR
    🟢 LOW:
    4. Clean desk
```

---

## Frontend UI Updates

### Task Form
- Date picker for due date
- Priority selector (High/Medium/Low)
- Tag input with autocomplete
- Recurrence selector (None/Daily/Weekly/Monthly/Custom)
- Reminder toggle with time selector

### Task List
- Priority badges (🔴🟡🟢)
- Due date display with overdue highlighting
- Tag chips
- Recurring icon (🔄)
- Search bar
- Filter dropdowns
- Sort selector

### Task Item
```
┌────────────────────────────────────────────────────────────┐
│ ☐ [🔴] Meeting prep                      Due: Today 3pm 🔔 │
│     #work #urgent                                     🔄    │
└────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

### Due Dates
- [ ] Can set due date when creating task
- [ ] Can update due date
- [ ] Due date displays correctly
- [ ] Overdue tasks highlighted

### Priorities
- [ ] Can set priority (High/Medium/Low)
- [ ] Priority badge displays correctly
- [ ] Can filter by priority

### Tags
- [ ] Can add tags to tasks
- [ ] Tags display as chips
- [ ] Can filter by tag
- [ ] Can create/delete tags

### Reminders
- [ ] Reminder scheduled via Dapr Jobs
- [ ] Notification Service receives event
- [ ] Reminder fires at correct time

### Recurring Tasks
- [ ] Can create recurring task
- [ ] Completing creates next occurrence
- [ ] Recurring icon displays
- [ ] Can set end date

### Search
- [ ] Full-text search works
- [ ] Results ranked by relevance

### Filter/Sort
- [ ] All filter options work
- [ ] All sort options work
- [ ] Combined filters work
