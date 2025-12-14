# Phase III Implementation Plan: AI Chatbot with MCP

> Detailed step-by-step implementation guide for the AI-powered chatbot interface

## Overview

This plan covers the full implementation of the natural language todo assistant using OpenAI Agents SDK and MCP (Model Context Protocol).

**References:**
- @specs/overview.md - Project overview and tech stack
- @specs/features/chatbot.md - Agent behavior specification
- @specs/mcp/tools.md - MCP tool definitions
- @specs/database/conversation-schema.md - Database models
- @specs/api/chat-endpoint.md - API specification

---

## Implementation Phases

| Phase | Component | Files | Priority |
|-------|-----------|-------|----------|
| 3.1 | Database Models & Migration | `backend/app/models/` | P0 |
| 3.2 | MCP Server & Tools | `backend/app/mcp/` | P0 |
| 3.3 | Agent Definition | `backend/app/agent/` | P0 |
| 3.4 | Chat API Endpoint | `backend/app/routers/chat.py` | P0 |
| 3.5 | Frontend Chat UI | `frontend/src/components/Chat/` | P0 |
| 3.6 | Integration & Testing | Tests + E2E | P1 |

---

## Phase 3.1: Database Models & Migration

### 3.1.1 Create Conversation Model

**File:** `backend/app/models/conversation.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """Chat conversation session."""

    __tablename__ = "conversation"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### 3.1.2 Create Message Model

**File:** `backend/app/models/message.py`

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "message"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str = Field(nullable=False)  # user, assistant, system, tool
    content: str = Field(nullable=False)
    tool_calls: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tool_call_id: Optional[str] = Field(default=None)
    metadata_: Optional[dict[str, Any]] = Field(default=None, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

### 3.1.3 Update Models __init__.py

**File:** `backend/app/models/__init__.py`

```python
from .task import Task
from .user import User
from .conversation import Conversation
from .message import Message

__all__ = ["Task", "User", "Conversation", "Message"]
```

### 3.1.4 Update Database Initialization

**File:** `backend/app/database.py` - Ensure models are imported so tables are created:

```python
from app.models import Task, User, Conversation, Message  # Add imports
```

### 3.1.5 Create Pydantic Schemas

**File:** `backend/app/schemas/chat.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    """Request schema for POST /api/chat"""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for POST /api/chat"""
    response: str
    conversation_id: str
    actions_taken: List[dict[str, Any]] = []
    metadata: Optional[dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Message in history response"""
    id: str
    role: str
    content: str
    tool_calls: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation in history response"""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """Response schema for GET /api/chat/history"""
    conversations: List[ConversationResponse]
    messages: List[MessageResponse] = []
    total: int
    has_more: bool = False
```

---

## Phase 3.2: MCP Server & Tools

### 3.2.1 Create MCP Tools Module

**File:** `backend/app/mcp/__init__.py`

```python
from .tools import (
    add_task,
    list_tasks,
    complete_task,
    update_task,
    delete_task,
    get_tools,
)

__all__ = [
    "add_task",
    "list_tasks",
    "complete_task",
    "update_task",
    "delete_task",
    "get_tools",
]
```

### 3.2.2 Implement MCP Tools

**File:** `backend/app/mcp/tools.py`

```python
"""
MCP Tools for Todo Management

Each tool receives user_id injected by the chat endpoint (never from AI).
Tools use SQLModel for database operations.
"""

from typing import Optional, Any
from sqlmodel import Session, select
from datetime import datetime

from app.database import engine
from app.models.task import Task


# Tool definitions for OpenAI Agents SDK
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
        return {
            "id": task.id,
            "title": task.title,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
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
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "completed": t.completed,
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat(),
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

        if not task:
            return {"success": False, "error": "Task not found"}

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat(),
            }
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

        if not task:
            return {"success": False, "error": "Task not found"}

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
                "updated_at": task.updated_at.isoformat(),
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
            return {"success": False, "error": "Must provide task_id, title_match, or delete_completed"}

        session.commit()

        return {
            "success": True,
            "deleted": deleted,
            "count": len(deleted)
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
    """Execute a tool with user_id injected for security."""
    if tool_name not in TOOL_HANDLERS:
        return {"error": f"Unknown tool: {tool_name}"}

    # Inject user_id - AI cannot override this
    arguments["user_id"] = user_id

    handler = TOOL_HANDLERS[tool_name]
    return handler(**arguments)
```

---

## Phase 3.3: Agent Definition

### 3.3.1 Create Agent Module

**File:** `backend/app/agent/__init__.py`

```python
from .runner import run_agent, SYSTEM_PROMPT

__all__ = ["run_agent", "SYSTEM_PROMPT"]
```

### 3.3.2 Implement Agent Runner

**File:** `backend/app/agent/runner.py`

```python
"""
OpenAI Agents SDK Runner for Todo Assistant

Handles conversation flow, tool calling, and response generation.
"""

import json
from typing import Any
from openai import OpenAI

from app.mcp.tools import get_tools, execute_tool


# System prompt defining agent behavior
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural conversation.

You have access to tools that let you add, list, complete, update, and delete tasks.

## Behavior Rules:
1. **Always confirm actions** - Tell the user what you did (e.g., "✅ Added task: 'buy groceries'")
2. **Be concise** - Keep responses short and actionable
3. **Handle errors gracefully** - If something fails, explain what went wrong helpfully
4. **Clarify ambiguity** - If multiple tasks match, ask the user to be more specific
5. **Provide context** - After actions, show task counts (e.g., "You now have 3 pending tasks")

## Response Format:
- Use ✅ for successful additions/completions
- Use 📋 for listing tasks
- Use ✏️ for updates
- Use 🗑️ for deletions
- Use ❌ for errors
- Use checkboxes: [ ] for pending, [x] for completed

## Examples:
- "Added task" → "✅ Added task: 'buy groceries'\n\nYou now have 3 tasks (2 pending, 1 completed)."
- "List tasks" → "📋 Your tasks:\n\n1. [ ] Buy groceries\n2. [x] Call mom\n\n2 tasks (1 pending, 1 completed)"
- "Task not found" → "❌ I couldn't find a task matching 'xyz'. Your current tasks are: ..."
"""


def run_agent(
    messages: list[dict[str, Any]],
    user_id: str,
    model: str = "gpt-4o-mini"
) -> tuple[str, list[dict[str, Any]]]:
    """
    Run the agent with conversation history and return response.

    Args:
        messages: List of conversation messages (OpenAI format)
        user_id: Authenticated user's ID (injected into tool calls)
        model: OpenAI model to use

    Returns:
        Tuple of (response_text, actions_taken)
    """
    client = OpenAI()
    tools = get_tools()
    actions_taken = []

    # Add system prompt if not present
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # Run conversation loop (handle tool calls)
    max_iterations = 10  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Check if we need to call tools
        if assistant_message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # Execute tool with user_id injection
                result = execute_tool(tool_name, arguments, user_id)

                # Track action
                actions_taken.append({
                    "tool": tool_name,
                    "input": arguments,
                    "result": result
                })

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        else:
            # No tool calls - return the response
            return assistant_message.content or "", actions_taken

    # Max iterations reached
    return "I'm having trouble processing your request. Please try again.", actions_taken
```

---

## Phase 3.4: Chat API Endpoint

### 3.4.1 Create Chat Router

**File:** `backend/app/routers/chat.py`

```python
"""
Chat API Endpoint

Handles conversation with the AI agent, including:
- Message processing
- Conversation history management
- Tool execution via MCP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional
import json

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    ConversationResponse,
    MessageResponse,
)
from app.agent.runner import run_agent


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> ChatResponse:
    """
    Process a chat message and return AI response.

    Flow:
    1. Get or create conversation
    2. Fetch conversation history
    3. Build messages for agent
    4. Run agent with MCP tools
    5. Store messages
    6. Return response
    """
    # 1. Get or create conversation
    if request.conversation_id:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # 2. Fetch conversation history
    history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()

    # 3. Build messages for agent
    messages = []
    for msg in history:
        msg_dict = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls
        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id
        messages.append(msg_dict)

    # Add new user message
    messages.append({"role": "user", "content": request.message})

    # 4. Run agent with MCP tools
    response_text, actions_taken = run_agent(messages, user_id)

    # 5. Store messages
    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    session.add(user_message)

    # Store assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tool_calls={"actions": actions_taken} if actions_taken else None
    )
    session.add(assistant_message)

    # Update conversation
    conversation.updated_at = datetime.utcnow()
    if not conversation.title:
        # Auto-generate title from first message
        conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")

    session.commit()

    # 6. Return response
    return ChatResponse(
        response=response_text,
        conversation_id=conversation.id,
        actions_taken=actions_taken,
        metadata={
            "message_count": len(history) + 2,
            "model": "gpt-4o-mini"
        }
    )


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    conversation_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> HistoryResponse:
    """Get conversation history for the authenticated user."""

    # Get conversations
    conv_query = select(Conversation).where(Conversation.user_id == user_id)
    if conversation_id:
        conv_query = conv_query.where(Conversation.id == conversation_id)
    conv_query = conv_query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)

    conversations = session.exec(conv_query).all()

    # Get messages if specific conversation requested
    messages = []
    if conversation_id:
        msg_query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = session.exec(msg_query).all()

    # Count total conversations
    total = session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).all()

    return HistoryResponse(
        conversations=[
            ConversationResponse(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=len([m for m in session.exec(
                    select(Message).where(Message.conversation_id == c.id)
                ).all()])
            )
            for c in conversations
        ],
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls,
                created_at=m.created_at
            )
            for m in messages
        ],
        total=len(total),
        has_more=len(total) > offset + limit
    )


@router.delete("/history")
async def clear_history(
    conversation_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> dict:
    """Clear conversation history."""

    if conversation_id:
        # Delete specific conversation
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Delete messages first (cascade should handle this, but be explicit)
        messages = session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        for msg in messages:
            session.delete(msg)

        session.delete(conversation)
        session.commit()

        return {
            "deleted": True,
            "conversations_deleted": 1,
            "messages_deleted": len(messages)
        }
    else:
        # Delete all conversations for user
        conversations = session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()

        total_messages = 0
        for conv in conversations:
            messages = session.exec(
                select(Message).where(Message.conversation_id == conv.id)
            ).all()
            total_messages += len(messages)
            for msg in messages:
                session.delete(msg)
            session.delete(conv)

        session.commit()

        return {
            "deleted": True,
            "conversations_deleted": len(conversations),
            "messages_deleted": total_messages
        }
```

### 3.4.2 Register Router in Main App

**File:** `backend/app/main.py` - Add:

```python
from app.routers import tasks, chat  # Add chat import

# Include routers
app.include_router(tasks.router)
app.include_router(chat.router)  # Add this line
```

---

## Phase 3.5: Frontend Chat UI

### 3.5.1 Create Chat API Client

**File:** `frontend/src/lib/chat-api.ts`

```typescript
import { api } from './api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: Record<string, unknown>;
  created_at: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  actions_taken: Array<{
    tool: string;
    input: Record<string, unknown>;
    result: Record<string, unknown>;
  }>;
  metadata?: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface HistoryResponse {
  conversations: Conversation[];
  messages: ChatMessage[];
  total: number;
  has_more: boolean;
}

export const chatApi = {
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    return api.request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  },

  async getHistory(conversationId?: string, limit = 50): Promise<HistoryResponse> {
    const params = new URLSearchParams();
    if (conversationId) params.set('conversation_id', conversationId);
    params.set('limit', limit.toString());

    return api.request<HistoryResponse>(`/api/chat/history?${params}`);
  },

  async clearHistory(conversationId?: string): Promise<{ deleted: boolean }> {
    const params = conversationId ? `?conversation_id=${conversationId}` : '';
    return api.request<{ deleted: boolean }>(`/api/chat/history${params}`, {
      method: 'DELETE',
    });
  },
};
```

### 3.5.2 Create Chat Component

**File:** `frontend/src/components/Chat/ChatWidget.tsx`

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { chatApi, ChatMessage, ChatResponse } from '@/lib/chat-api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(
        userMessage.content,
        conversationId || undefined
      );

      setConversationId(response.conversation_id);

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '❌ Sorry, something went wrong. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (conversationId) {
      await chatApi.clearHistory(conversationId);
    }
    setMessages([]);
    setConversationId(null);
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors flex items-center justify-center z-50"
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 w-96 h-[500px] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-50">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-blue-600 text-white rounded-t-lg">
            <h3 className="font-semibold">Todo Assistant</h3>
            <button
              onClick={handleClearChat}
              className="text-sm hover:underline"
            >
              Clear
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-lg mb-2">👋 Hi! I'm your todo assistant.</p>
                <p className="text-sm">Try saying:</p>
                <p className="text-sm text-blue-600">"Add buy groceries"</p>
                <p className="text-sm text-blue-600">"Show my tasks"</p>
                <p className="text-sm text-blue-600">"Mark groceries as done"</p>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg whitespace-pre-wrap ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
```

### 3.5.3 Add Chat Widget to Dashboard

**File:** `frontend/src/app/dashboard/page.tsx` - Add import and component:

```typescript
import ChatWidget from '@/components/Chat/ChatWidget';

// ... existing code ...

return (
  <div>
    {/* Existing dashboard content */}

    {/* Add Chat Widget */}
    <ChatWidget />
  </div>
);
```

### 3.5.4 Export Chat Component

**File:** `frontend/src/components/Chat/index.ts`

```typescript
export { default as ChatWidget } from './ChatWidget';
```

---

## Phase 3.6: Integration & Testing

### 3.6.1 Backend Tests

**File:** `backend/tests/test_chat.py`

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


client = TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication to return a test user_id."""
    with patch("app.routers.chat.get_current_user_id") as mock:
        mock.return_value = "test-user-123"
        yield mock


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    with patch("app.agent.runner.OpenAI") as mock:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "✅ Added task: 'test task'"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock


def test_chat_endpoint(mock_auth, mock_openai):
    """Test POST /api/chat creates conversation and returns response."""
    response = client.post(
        "/api/chat",
        json={"message": "Add a test task"},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data


def test_chat_history(mock_auth):
    """Test GET /api/chat/history returns conversations."""
    response = client.get(
        "/api/chat/history",
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "total" in data
```

### 3.6.2 MCP Tools Tests

**File:** `backend/tests/test_mcp_tools.py`

```python
import pytest
from app.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task


@pytest.fixture
def test_user_id():
    return "test-user-for-mcp"


def test_add_task(test_user_id):
    """Test add_task creates a task."""
    result = add_task("Test MCP task", test_user_id)

    assert "id" in result
    assert result["title"] == "Test MCP task"
    assert result["completed"] == False


def test_list_tasks(test_user_id):
    """Test list_tasks returns user's tasks."""
    # Add a task first
    add_task("List test task", test_user_id)

    result = list_tasks(test_user_id)

    assert "tasks" in result
    assert "total" in result
    assert result["total"] >= 1


def test_complete_task_by_title(test_user_id):
    """Test complete_task by title match."""
    # Add a task
    task = add_task("Complete me", test_user_id)

    result = complete_task(test_user_id, title_match="Complete")

    assert result["success"] == True
    assert result["task"]["completed"] == True


def test_update_task(test_user_id):
    """Test update_task changes title."""
    # Add a task
    task = add_task("Old title", test_user_id)

    result = update_task(test_user_id, "New title", title_match="Old")

    assert result["success"] == True
    assert result["task"]["title"] == "New title"
    assert result["task"]["previous_title"] == "Old title"


def test_delete_task(test_user_id):
    """Test delete_task removes task."""
    # Add a task
    task = add_task("Delete me", test_user_id)

    result = delete_task(test_user_id, title_match="Delete")

    assert result["success"] == True
    assert result["count"] == 1
```

---

## File Summary

### New Backend Files

| File | Description |
|------|-------------|
| `backend/app/models/conversation.py` | Conversation SQLModel |
| `backend/app/models/message.py` | Message SQLModel |
| `backend/app/schemas/chat.py` | Chat Pydantic schemas |
| `backend/app/mcp/__init__.py` | MCP module init |
| `backend/app/mcp/tools.py` | MCP tool implementations |
| `backend/app/agent/__init__.py` | Agent module init |
| `backend/app/agent/runner.py` | OpenAI agent runner |
| `backend/app/routers/chat.py` | Chat API endpoints |
| `backend/tests/test_chat.py` | Chat endpoint tests |
| `backend/tests/test_mcp_tools.py` | MCP tools tests |

### New Frontend Files

| File | Description |
|------|-------------|
| `frontend/src/lib/chat-api.ts` | Chat API client |
| `frontend/src/components/Chat/ChatWidget.tsx` | Chat UI component |
| `frontend/src/components/Chat/index.ts` | Chat component export |

### Modified Files

| File | Change |
|------|--------|
| `backend/app/models/__init__.py` | Add Conversation, Message exports |
| `backend/app/main.py` | Register chat router |
| `frontend/src/app/dashboard/page.tsx` | Add ChatWidget |

---

## Deployment Checklist

- [ ] Run database migrations (tables auto-create via SQLModel)
- [ ] Set `OPENAI_API_KEY` in production environment
- [ ] Test all MCP tools with real database
- [ ] Test chat endpoint with authentication
- [ ] Verify user isolation (user A can't see user B's data)
- [ ] Test frontend chat widget
- [ ] Monitor OpenAI API usage and costs
- [ ] Set up rate limiting for chat endpoint

---

## Next Steps After Implementation

1. Add streaming responses (SSE) for better UX
2. Implement conversation search
3. Add conversation export feature
4. Implement rate limiting
5. Add analytics/monitoring
6. Consider voice input support
