# MCP Tools Specification

> Model Context Protocol tools for todo management

## Overview

The MCP server exposes tools that allow the AI agent to perform CRUD operations on tasks. Each tool enforces user isolation via the `user_id` parameter derived from the authenticated session.

## Tool Registry

| Tool Name | Description | Idempotent |
|-----------|-------------|------------|
| `add_task` | Create a new task | No |
| `list_tasks` | List user's tasks with optional filters | Yes |
| `complete_task` | Mark a task as completed | Yes |
| `update_task` | Modify a task's title | No |
| `delete_task` | Remove a task | No |

---

## add_task

Create a new task for the authenticated user.

### Tool Definition

```json
{
  "name": "add_task",
  "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "The task title/description",
        "minLength": 1,
        "maxLength": 500
      }
    },
    "required": ["title"]
  }
}
```

### Internal Parameters (injected by server)

| Parameter | Type | Source | Description |
|-----------|------|--------|-------------|
| `user_id` | string | JWT `sub` claim | Owner of the task |

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "title": {"type": "string"},
    "completed": {"type": "boolean"},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"}
  }
}
```

### Example

**Input:**
```json
{"title": "Buy groceries"}
```

**Output:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "completed": false,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## list_tasks

Retrieve tasks for the authenticated user with optional filters.

### Tool Definition

```json
{
  "name": "list_tasks",
  "description": "List the user's tasks. Can filter by completion status. Use this when the user wants to see, view, or check their tasks.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter tasks by status"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 50,
        "description": "Maximum number of tasks to return"
      },
      "search": {
        "type": "string",
        "description": "Search tasks by title (case-insensitive)"
      }
    },
    "required": []
  }
}
```

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "title": {"type": "string"},
          "completed": {"type": "boolean"},
          "created_at": {"type": "string"},
          "updated_at": {"type": "string"}
        }
      }
    },
    "total": {"type": "integer"},
    "pending_count": {"type": "integer"},
    "completed_count": {"type": "integer"}
  }
}
```

### Example

**Input:**
```json
{"status": "pending"}
```

**Output:**
```json
{
  "tasks": [
    {"id": "uuid-1", "title": "Buy groceries", "completed": false, "created_at": "...", "updated_at": "..."},
    {"id": "uuid-2", "title": "Call mom", "completed": false, "created_at": "...", "updated_at": "..."}
  ],
  "total": 2,
  "pending_count": 2,
  "completed_count": 0
}
```

---

## complete_task

Mark a task as completed.

### Tool Definition

```json
{
  "name": "complete_task",
  "description": "Mark a task as completed/done. Use this when the user says they finished, completed, or done with a task.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "The UUID of the task to complete"
      },
      "title_match": {
        "type": "string",
        "description": "Partial title to match (case-insensitive). Use if task_id is unknown."
      }
    },
    "oneOf": [
      {"required": ["task_id"]},
      {"required": ["title_match"]}
    ]
  }
}
```

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "completed": {"type": "boolean"},
        "updated_at": {"type": "string"}
      }
    },
    "error": {"type": "string"}
  }
}
```

### Example

**Input (by title match):**
```json
{"title_match": "groceries"}
```

**Output:**
```json
{
  "success": true,
  "task": {
    "id": "uuid-1",
    "title": "Buy groceries",
    "completed": true,
    "updated_at": "2025-01-15T11:00:00Z"
  }
}
```

### Error Cases

**Multiple matches:**
```json
{
  "success": false,
  "error": "Multiple tasks match 'call'. Please be more specific.",
  "matches": [
    {"id": "uuid-1", "title": "Call mom"},
    {"id": "uuid-2", "title": "Call dentist"}
  ]
}
```

**No match:**
```json
{
  "success": false,
  "error": "No task found matching 'xyz'"
}
```

---

## update_task

Modify a task's title.

### Tool Definition

```json
{
  "name": "update_task",
  "description": "Update/rename a task's title. Use this when the user wants to change, rename, or modify a task.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "The UUID of the task to update"
      },
      "title_match": {
        "type": "string",
        "description": "Partial title to match (case-insensitive). Use if task_id is unknown."
      },
      "new_title": {
        "type": "string",
        "description": "The new title for the task",
        "minLength": 1,
        "maxLength": 500
      }
    },
    "required": ["new_title"],
    "oneOf": [
      {"required": ["task_id", "new_title"]},
      {"required": ["title_match", "new_title"]}
    ]
  }
}
```

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "previous_title": {"type": "string"},
        "completed": {"type": "boolean"},
        "updated_at": {"type": "string"}
      }
    },
    "error": {"type": "string"}
  }
}
```

### Example

**Input:**
```json
{
  "title_match": "groceries",
  "new_title": "Buy groceries and vegetables"
}
```

**Output:**
```json
{
  "success": true,
  "task": {
    "id": "uuid-1",
    "title": "Buy groceries and vegetables",
    "previous_title": "Buy groceries",
    "completed": false,
    "updated_at": "2025-01-15T11:30:00Z"
  }
}
```

---

## delete_task

Remove a task permanently.

### Tool Definition

```json
{
  "name": "delete_task",
  "description": "Delete/remove a task permanently. Use this when the user wants to delete, remove, or clear a task.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "The UUID of the task to delete"
      },
      "title_match": {
        "type": "string",
        "description": "Partial title to match (case-insensitive). Use if task_id is unknown."
      },
      "delete_completed": {
        "type": "boolean",
        "default": false,
        "description": "If true, delete all completed tasks"
      }
    },
    "oneOf": [
      {"required": ["task_id"]},
      {"required": ["title_match"]},
      {"required": ["delete_completed"]}
    ]
  }
}
```

### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "deleted": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "title": {"type": "string"}
        }
      }
    },
    "count": {"type": "integer"},
    "error": {"type": "string"}
  }
}
```

### Example

**Input (single task):**
```json
{"title_match": "groceries"}
```

**Output:**
```json
{
  "success": true,
  "deleted": [{"id": "uuid-1", "title": "Buy groceries"}],
  "count": 1
}
```

**Input (all completed):**
```json
{"delete_completed": true}
```

**Output:**
```json
{
  "success": true,
  "deleted": [
    {"id": "uuid-3", "title": "Old task 1"},
    {"id": "uuid-4", "title": "Old task 2"}
  ],
  "count": 2
}
```

---

## Security Model

### User Isolation

All tools automatically inject `user_id` from the authenticated session:

```python
# Pseudo-code: Tool execution wrapper
async def execute_tool(tool_name: str, input: dict, user_id: str):
    # user_id is NEVER provided by the AI - always from auth
    input["user_id"] = user_id
    return await tools[tool_name].execute(input)
```

### Authorization Rules

| Rule | Implementation |
|------|----------------|
| User can only access own tasks | `WHERE user_id = :user_id` on all queries |
| AI cannot override user_id | Parameter injected server-side |
| Cross-user access blocked | 403 Forbidden if task.user_id != session.user_id |

---

## MCP Server Registration

```python
from mcp import Server, Tool

server = Server("todo-mcp")

@server.tool()
async def add_task(title: str, user_id: str) -> dict:
    """Create a new task"""
    ...

@server.tool()
async def list_tasks(status: str = "all", user_id: str) -> dict:
    """List tasks with optional filter"""
    ...

@server.tool()
async def complete_task(task_id: str = None, title_match: str = None, user_id: str) -> dict:
    """Mark a task as completed"""
    ...

@server.tool()
async def update_task(new_title: str, task_id: str = None, title_match: str = None, user_id: str) -> dict:
    """Update a task's title"""
    ...

@server.tool()
async def delete_task(task_id: str = None, title_match: str = None, delete_completed: bool = False, user_id: str) -> dict:
    """Delete a task"""
    ...
```
