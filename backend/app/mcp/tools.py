"""
MCP Tools for Todo Management

Each tool receives user_id injected by the chat endpoint (never from AI).
Tools use SQLModel for database operations.
Stateless design - each call creates its own session.
"""

from typing import Optional, Any
from sqlmodel import Session, select
from datetime import datetime

from app.database import engine
from app.models.task import Task


# Tool definitions for OpenAI Agents SDK (function calling format)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title/description"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks. Can filter by completion status. Use this when the user wants to see, view, or check their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status. Default is 'all'."
                    },
                    "search": {
                        "type": "string",
                        "description": "Search tasks by title (case-insensitive)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed/done. Use this when the user says they finished, completed, or done with a task.",
            "parameters": {
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
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update/rename a task's title. Use this when the user wants to change, rename, or modify a task.",
            "parameters": {
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
                        "description": "The new title for the task"
                    }
                },
                "required": ["new_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete/remove a task permanently. Use this when the user wants to delete, remove, or clear a task.",
            "parameters": {
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
                        "description": "If true, delete all completed tasks"
                    }
                },
                "required": []
            }
        }
    }
]


def get_tools() -> list[dict]:
    """Return tool definitions for OpenAI Agents SDK."""
    return TOOL_DEFINITIONS


def add_task(title: str, user_id: str) -> dict[str, Any]:
    """Create a new task for the user."""
    with Session(engine) as session:
        task = Task(title=title, user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)

        # Get updated counts
        all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
            },
            "total_tasks": len(all_tasks),
            "pending_count": pending_count,
            "completed_count": completed_count,
        }


def list_tasks(
    user_id: str,
    status: str = "all",
    search: Optional[str] = None,
    limit: int = 50
) -> dict[str, Any]:
    """List tasks for the user with optional filters."""
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        if search:
            statement = statement.where(Task.title.ilike(f"%{search}%"))

        statement = statement.order_by(Task.created_at.desc()).limit(limit)
        tasks = session.exec(statement).all()

        # Count totals
        all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)

        return {
            "success": True,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "completed": t.completed,
                    "created_at": t.created_at.isoformat(),
                }
                for t in tasks
            ],
            "total": len(all_tasks),
            "pending_count": pending_count,
            "completed_count": completed_count,
        }


def complete_task(
    user_id: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None
) -> dict[str, Any]:
    """Mark a task as completed."""
    with Session(engine) as session:
        # Find task by ID or title match
        if task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if not task:
                return {"success": False, "error": "Task not found"}
        elif title_match:
            tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(f"%{title_match}%"),
                    Task.completed == False  # Only match pending tasks
                )
            ).all()

            if len(tasks) == 0:
                return {"success": False, "error": f"No pending task found matching '{title_match}'"}
            elif len(tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks match '{title_match}'. Please be more specific.",
                    "matches": [{"id": t.id, "title": t.title} for t in tasks]
                }
            task = tasks[0]
        else:
            return {"success": False, "error": "Must provide task_id or title_match"}

        if task.completed:
            return {"success": False, "error": f"Task '{task.title}' is already completed"}

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        # Get updated counts
        all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
            },
            "pending_count": pending_count,
            "completed_count": completed_count,
        }


def update_task(
    user_id: str,
    new_title: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None
) -> dict[str, Any]:
    """Update a task's title."""
    with Session(engine) as session:
        # Find task by ID or title match
        if task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if not task:
                return {"success": False, "error": "Task not found"}
        elif title_match:
            tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(f"%{title_match}%")
                )
            ).all()

            if len(tasks) == 0:
                return {"success": False, "error": f"No task found matching '{title_match}'"}
            elif len(tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks match '{title_match}'. Please be more specific.",
                    "matches": [{"id": t.id, "title": t.title} for t in tasks]
                }
            task = tasks[0]
        else:
            return {"success": False, "error": "Must provide task_id or title_match"}

        previous_title = task.title
        task.title = new_title
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "previous_title": previous_title,
                "completed": task.completed,
            }
        }


def delete_task(
    user_id: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None,
    delete_completed: bool = False
) -> dict[str, Any]:
    """Delete a task permanently."""
    with Session(engine) as session:
        deleted = []

        if delete_completed:
            # Delete all completed tasks
            tasks = session.exec(
                select(Task).where(Task.user_id == user_id, Task.completed == True)
            ).all()
            for task in tasks:
                deleted.append({"id": task.id, "title": task.title})
                session.delete(task)
        elif task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if task:
                deleted.append({"id": task.id, "title": task.title})
                session.delete(task)
            else:
                return {"success": False, "error": "Task not found"}
        elif title_match:
            tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(f"%{title_match}%")
                )
            ).all()

            if len(tasks) == 0:
                return {"success": False, "error": f"No task found matching '{title_match}'"}
            elif len(tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks match '{title_match}'. Please be more specific.",
                    "matches": [{"id": t.id, "title": t.title} for t in tasks]
                }

            deleted.append({"id": tasks[0].id, "title": tasks[0].title})
            session.delete(tasks[0])
        else:
            return {"success": False, "error": "Must provide task_id, title_match, or delete_completed=true"}

        session.commit()

        # Get updated counts
        all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)

        return {
            "success": True,
            "deleted": deleted,
            "count": len(deleted),
            "remaining_tasks": len(all_tasks),
            "pending_count": pending_count,
            "completed_count": completed_count,
        }


# Tool dispatcher for agent
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "update_task": update_task,
    "delete_task": delete_task,
}


def execute_tool(tool_name: str, arguments: dict, user_id: str) -> dict[str, Any]:
    """
    Execute a tool with user_id injected for security.

    The user_id is ALWAYS injected server-side from the authenticated session.
    The AI cannot override or provide user_id.
    """
    if tool_name not in TOOL_HANDLERS:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    # Inject user_id - AI cannot override this
    arguments["user_id"] = user_id

    handler = TOOL_HANDLERS[tool_name]
    try:
        return handler(**arguments)
    except Exception as e:
        return {"success": False, "error": str(e)}
