"""
MCP Tools for Todo Management - Phase V

Each tool receives user_id injected by the chat endpoint (never from AI).
Tools use SQLModel for database operations.
Stateless design - each call creates its own session.

Phase V additions:
- Due dates, priorities, tags, recurrence support
- Filtering by priority, tag, overdue status
- Sorting options
"""

from typing import Optional, Any
from sqlmodel import Session, select
from sqlalchemy import desc, asc
from datetime import datetime

from app.database import engine
from app.models.task import Task
from app.models.tag import Tag, TaskTag


# Tool definitions for OpenAI Agents SDK (function calling format)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something. Can include due date, priority (1=High, 2=Medium, 3=Low), and tags.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title/description"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format (e.g., '2025-12-31T23:59:59'). Optional."
                    },
                    "priority": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                        "description": "Priority level: 1=High, 2=Medium, 3=Low. Optional."
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tag names to attach (will be created if they don't exist). Optional."
                    },
                    "recurrence_rule": {
                        "type": "string",
                        "description": "iCal RRULE format for recurring tasks (e.g., 'FREQ=DAILY' or 'FREQ=WEEKLY;BYDAY=MO'). Optional."
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
            "description": "List the user's tasks with optional filters. Can filter by status, priority, tag, search text, or overdue. Can sort by due_date, priority, title, or created_at.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status. Default is 'all'."
                    },
                    "priority": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                        "description": "Filter by priority: 1=High, 2=Medium, 3=Low"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by tag name"
                    },
                    "search": {
                        "type": "string",
                        "description": "Search tasks by title (case-insensitive)"
                    },
                    "overdue": {
                        "type": "boolean",
                        "description": "If true, only show overdue tasks (past due_date, not completed)"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["due_date", "priority", "title", "created_at"],
                        "description": "Sort field. Default is 'created_at'."
                    },
                    "sort_order": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Sort order. Default is 'desc'."
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
            "description": "Update a task's title, due date, priority, or tags. Use this when the user wants to change, rename, or modify a task.",
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
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO format (e.g., '2025-12-31T23:59:59')"
                    },
                    "priority": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                        "description": "New priority: 1=High, 2=Medium, 3=Low"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Replace all tags with these tag names"
                    }
                },
                "required": []
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
    },
    {
        "type": "function",
        "function": {
            "name": "manage_tags",
            "description": "Create, list, or delete tags. Tags are used to categorize tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "delete"],
                        "description": "Action to perform"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tag name (required for create/delete)"
                    },
                    "color": {
                        "type": "string",
                        "description": "Hex color code for the tag (e.g., '#FF5733'). Default is gray."
                    }
                },
                "required": ["action"]
            }
        }
    }
]


def get_tools() -> list[dict]:
    """Return tool definitions for OpenAI Agents SDK."""
    return TOOL_DEFINITIONS


def _get_or_create_tag(session: Session, tag_name: str, user_id: str) -> Tag:
    """Get an existing tag or create a new one."""
    tag = session.exec(
        select(Tag).where(Tag.name == tag_name, Tag.user_id == user_id)
    ).first()
    if not tag:
        tag = Tag(name=tag_name, user_id=user_id)
        session.add(tag)
        session.commit()
        session.refresh(tag)
    return tag


def _get_task_tags(session: Session, task_id: str) -> list[dict]:
    """Get tags for a task."""
    tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    return [{"id": t.id, "name": t.name, "color": t.color} for t in tags]


def _task_to_dict(task: Task, session: Session) -> dict:
    """Convert task to dictionary with tags."""
    return {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "priority_label": {1: "High", 2: "Medium", 3: "Low"}.get(task.priority),
        "recurrence_rule": task.recurrence_rule,
        "tags": _get_task_tags(session, task.id),
    }


def add_task(
    title: str,
    user_id: str,
    due_date: Optional[str] = None,
    priority: Optional[int] = None,
    tags: Optional[list[str]] = None,
    recurrence_rule: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new task for the user with optional Phase V fields."""
    with Session(engine) as session:
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {"success": False, "error": f"Invalid due_date format: {due_date}"}

        task = Task(
            title=title,
            user_id=user_id,
            due_date=parsed_due_date,
            priority=priority,
            recurrence_rule=recurrence_rule,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Attach tags if provided
        if tags:
            for tag_name in tags:
                tag = _get_or_create_tag(session, tag_name, user_id)
                task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                session.add(task_tag)
            session.commit()

        # Get updated counts
        all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)

        return {
            "success": True,
            "task": _task_to_dict(task, session),
            "total_tasks": len(all_tasks),
            "pending_count": pending_count,
            "completed_count": completed_count,
        }


def list_tasks(
    user_id: str,
    status: str = "all",
    priority: Optional[int] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    overdue: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 50
) -> dict[str, Any]:
    """List tasks for the user with optional filters and sorting."""
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        # Status filter
        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        # Priority filter
        if priority is not None:
            statement = statement.where(Task.priority == priority)

        # Tag filter
        if tag:
            tag_obj = session.exec(
                select(Tag).where(Tag.name == tag, Tag.user_id == user_id)
            ).first()
            if tag_obj:
                statement = statement.join(TaskTag).where(TaskTag.tag_id == tag_obj.id)
            else:
                return {"success": True, "tasks": [], "total": 0, "message": f"No tag named '{tag}' found"}

        # Search filter
        if search:
            statement = statement.where(Task.title.ilike(f"%{search}%"))

        # Overdue filter
        if overdue:
            now = datetime.utcnow()
            statement = statement.where(
                Task.due_date < now,
                Task.completed == False
            )

        # Sorting
        sort_column = {
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "created_at": Task.created_at,
        }.get(sort_by, Task.created_at)

        if sort_order == "asc":
            statement = statement.order_by(asc(sort_column))
        else:
            statement = statement.order_by(desc(sort_column))

        statement = statement.limit(limit)
        tasks = session.exec(statement).all()

        # Count totals
        all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        completed_count = sum(1 for t in all_tasks if t.completed)
        overdue_count = sum(
            1 for t in all_tasks
            if t.due_date and t.due_date < datetime.utcnow() and not t.completed
        )

        return {
            "success": True,
            "tasks": [_task_to_dict(t, session) for t in tasks],
            "total": len(all_tasks),
            "pending_count": pending_count,
            "completed_count": completed_count,
            "overdue_count": overdue_count,
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
            "task": _task_to_dict(task, session),
            "pending_count": pending_count,
            "completed_count": completed_count,
        }


def update_task(
    user_id: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None,
    new_title: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[int] = None,
    tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Update a task's fields."""
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

        changes = {}

        # Update title
        if new_title:
            changes["title"] = {"from": task.title, "to": new_title}
            task.title = new_title

        # Update due_date
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                changes["due_date"] = {"to": due_date}
                task.due_date = parsed_due_date
            except ValueError:
                return {"success": False, "error": f"Invalid due_date format: {due_date}"}

        # Update priority
        if priority is not None:
            changes["priority"] = {"from": task.priority, "to": priority}
            task.priority = priority

        # Update tags
        if tags is not None:
            # Remove existing tags
            existing_task_tags = session.exec(
                select(TaskTag).where(TaskTag.task_id == task.id)
            ).all()
            for tt in existing_task_tags:
                session.delete(tt)

            # Add new tags
            for tag_name in tags:
                tag = _get_or_create_tag(session, tag_name, user_id)
                task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                session.add(task_tag)
            changes["tags"] = {"to": tags}

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task": _task_to_dict(task, session),
            "changes": changes,
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
                # Delete task_tags first
                task_tags = session.exec(
                    select(TaskTag).where(TaskTag.task_id == task.id)
                ).all()
                for tt in task_tags:
                    session.delete(tt)
                deleted.append({"id": task.id, "title": task.title})
                session.delete(task)
        elif task_id:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()
            if task:
                # Delete task_tags first
                task_tags = session.exec(
                    select(TaskTag).where(TaskTag.task_id == task.id)
                ).all()
                for tt in task_tags:
                    session.delete(tt)
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

            # Delete task_tags first
            task_tags = session.exec(
                select(TaskTag).where(TaskTag.task_id == tasks[0].id)
            ).all()
            for tt in task_tags:
                session.delete(tt)
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


def manage_tags(
    user_id: str,
    action: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
) -> dict[str, Any]:
    """Manage tags - list, create, or delete."""
    with Session(engine) as session:
        if action == "list":
            tags = session.exec(
                select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
            ).all()
            return {
                "success": True,
                "tags": [
                    {"id": t.id, "name": t.name, "color": t.color}
                    for t in tags
                ],
                "count": len(tags),
            }

        elif action == "create":
            if not name:
                return {"success": False, "error": "Tag name is required"}

            # Check if exists
            existing = session.exec(
                select(Tag).where(Tag.name == name, Tag.user_id == user_id)
            ).first()
            if existing:
                return {"success": False, "error": f"Tag '{name}' already exists"}

            tag = Tag(
                name=name,
                color=color or "#6B7280",
                user_id=user_id,
            )
            session.add(tag)
            session.commit()
            session.refresh(tag)

            return {
                "success": True,
                "tag": {"id": tag.id, "name": tag.name, "color": tag.color},
            }

        elif action == "delete":
            if not name:
                return {"success": False, "error": "Tag name is required"}

            tag = session.exec(
                select(Tag).where(Tag.name == name, Tag.user_id == user_id)
            ).first()
            if not tag:
                return {"success": False, "error": f"Tag '{name}' not found"}

            # Delete task_tags first
            task_tags = session.exec(
                select(TaskTag).where(TaskTag.tag_id == tag.id)
            ).all()
            for tt in task_tags:
                session.delete(tt)

            session.delete(tag)
            session.commit()

            return {
                "success": True,
                "deleted": {"id": tag.id, "name": tag.name},
            }

        else:
            return {"success": False, "error": f"Unknown action: {action}"}


# Tool dispatcher for agent
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "manage_tags": manage_tags,
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
