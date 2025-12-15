"""
MCP Server for Todo Assistant

Exposes task management tools via Model Context Protocol (MCP).
Uses FastMCP with Streamable HTTP transport for agent communication.

The server wraps existing tool implementations from tools.py and
exposes them via the standard MCP protocol for automatic discovery.
"""

from contextlib import asynccontextmanager
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP

from app.mcp.tools import execute_tool


# Initialize MCP server with stateless HTTP mode
# stateless_http=True ensures each request is independent (no session state)
mcp = FastMCP(
    "Todo Assistant",
    stateless_http=True,
    instructions="""You are a helpful todo assistant. You help users manage their tasks.

Available operations:
- add_task: Create new tasks
- list_tasks: View tasks with optional filters
- complete_task: Mark tasks as done
- update_task: Change task titles
- delete_task: Remove tasks

Always confirm actions and provide task counts after changes."""
)


@mcp.tool()
def add_task(title: str, user_id: str) -> dict[str, Any]:
    """
    Create a new task for the user.

    Use this when the user wants to add, create, or remember something.

    Args:
        title: The task title/description
        user_id: The authenticated user's ID (injected by system)

    Returns:
        Success status with task details and updated counts
    """
    return execute_tool("add_task", {"title": title}, user_id)


@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    search: Optional[str] = None
) -> dict[str, Any]:
    """
    List the user's tasks with optional filters.

    Use this when the user wants to see, view, or check their tasks.

    Args:
        user_id: The authenticated user's ID (injected by system)
        status: Filter by status - "all", "pending", or "completed"
        search: Search tasks by title (case-insensitive)

    Returns:
        List of tasks with counts
    """
    return execute_tool("list_tasks", {"status": status, "search": search}, user_id)


@mcp.tool()
def complete_task(
    user_id: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None
) -> dict[str, Any]:
    """
    Mark a task as completed/done.

    Use this when the user says they finished, completed, or are done with a task.
    Can identify task by ID or by matching title text.

    Args:
        user_id: The authenticated user's ID (injected by system)
        task_id: The UUID of the task to complete (if known)
        title_match: Partial title to match (case-insensitive, use if task_id unknown)

    Returns:
        Success status with updated task and counts
    """
    return execute_tool(
        "complete_task",
        {"task_id": task_id, "title_match": title_match},
        user_id
    )


@mcp.tool()
def update_task(
    user_id: str,
    new_title: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None
) -> dict[str, Any]:
    """
    Update/rename a task's title.

    Use this when the user wants to change, rename, or modify a task.
    Can identify task by ID or by matching title text.

    Args:
        user_id: The authenticated user's ID (injected by system)
        new_title: The new title for the task
        task_id: The UUID of the task to update (if known)
        title_match: Partial title to match (case-insensitive, use if task_id unknown)

    Returns:
        Success status with updated task details
    """
    return execute_tool(
        "update_task",
        {"task_id": task_id, "title_match": title_match, "new_title": new_title},
        user_id
    )


@mcp.tool()
def delete_task(
    user_id: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None,
    delete_completed: bool = False
) -> dict[str, Any]:
    """
    Delete/remove a task permanently.

    Use this when the user wants to delete, remove, or clear a task.
    Can delete by ID, by title match, or all completed tasks.

    Args:
        user_id: The authenticated user's ID (injected by system)
        task_id: The UUID of the task to delete (if known)
        title_match: Partial title to match (case-insensitive, use if task_id unknown)
        delete_completed: If true, delete all completed tasks

    Returns:
        Success status with deletion details and remaining counts
    """
    return execute_tool(
        "delete_task",
        {"task_id": task_id, "title_match": title_match, "delete_completed": delete_completed},
        user_id
    )


@asynccontextmanager
async def mcp_lifespan(app):
    """
    Lifespan context manager for MCP server.

    Ensures proper initialization and cleanup of MCP session manager.
    Use this in FastAPI's lifespan parameter.
    """
    async with mcp.session_manager.run():
        yield


def get_mcp_app():
    """
    Get the MCP ASGI application for mounting on FastAPI.

    Returns an ASGI app that handles Streamable HTTP transport
    for MCP protocol communication.

    Usage:
        app.mount("/mcp", get_mcp_app())
    """
    return mcp.streamable_http_app()


# Export for use in main.py
__all__ = ["mcp", "mcp_lifespan", "get_mcp_app"]
