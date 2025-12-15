"""
ChatKit API Endpoint

SSE streaming endpoint compatible with OpenAI ChatKit frontend component.
Supports both synchronous and streaming responses for AI chat interactions.

Flow:
1. Receive ChatKit message request
2. Run agent with MCP tools
3. Stream response events via SSE (NDJSON format)
"""

import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.models.conversation import Conversation
from app.models.message import Message
from app.agent.runner import run_agent


router = APIRouter(prefix="/api/chatkit", tags=["chatkit"])


# ChatKit request/response models
class ChatKitMessage(BaseModel):
    """Message format for ChatKit."""
    role: str  # "user" or "assistant"
    content: str


class ChatKitRequest(BaseModel):
    """Request schema for ChatKit endpoint."""
    message: str
    thread_id: Optional[str] = None
    messages: Optional[list[ChatKitMessage]] = None


class ChatKitEvent(BaseModel):
    """SSE event for ChatKit streaming."""
    type: str
    data: dict


def create_sse_event(event_type: str, data: dict) -> str:
    """
    Format an SSE event in NDJSON format for ChatKit.

    Args:
        event_type: The type of event (e.g., "thread.created", "message.delta")
        data: The event data payload

    Returns:
        Formatted SSE event string
    """
    event_data = {"type": event_type, **data}
    return f"data: {json.dumps(event_data)}\n\n"


async def stream_chat_response(
    message: str,
    thread_id: str,
    user_id: str,
    session: Session,
) -> AsyncGenerator[str, None]:
    """
    Generate SSE events for ChatKit streaming response.

    Yields events in the format expected by ChatKit:
    - thread.created (if new thread)
    - message.created (user message)
    - message.created (assistant response start)
    - message.delta (content chunks - simplified to single chunk)
    - message.done (completion signal)
    - tool_call (for each tool invocation)

    Args:
        message: The user's message
        thread_id: The conversation thread ID
        user_id: The authenticated user's ID
        session: Database session

    Yields:
        SSE event strings in NDJSON format
    """
    # Get or create conversation
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == thread_id,
            Conversation.user_id == user_id
        )
    ).first()

    is_new_thread = conversation is None
    if is_new_thread:
        conversation = Conversation(id=thread_id, user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Emit thread.created event
        yield create_sse_event("thread.created", {
            "thread_id": thread_id,
            "created_at": datetime.utcnow().isoformat(),
        })

    # Fetch conversation history
    history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()

    # Build messages for agent
    messages = []
    for msg in history:
        if msg.role in ("user", "assistant"):
            messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": message})

    # Emit user message event
    user_msg_id = str(uuid.uuid4())
    yield create_sse_event("message.created", {
        "message_id": user_msg_id,
        "thread_id": thread_id,
        "role": "user",
        "content": message,
        "created_at": datetime.utcnow().isoformat(),
    })

    # Run agent
    try:
        response_text, actions_taken = await run_agent(messages, user_id)
    except Exception as e:
        response_text = f"Sorry, I encountered an error: {str(e)}"
        actions_taken = []

    # Emit tool call events
    for action in actions_taken:
        tool_id = str(uuid.uuid4())
        yield create_sse_event("tool_call", {
            "tool_call_id": tool_id,
            "tool_name": action.get("tool", "unknown"),
            "arguments": action.get("input", {}),
            "result": action.get("result", {}),
        })

    # Emit assistant message start
    assistant_msg_id = str(uuid.uuid4())
    yield create_sse_event("message.created", {
        "message_id": assistant_msg_id,
        "thread_id": thread_id,
        "role": "assistant",
        "content": "",
        "created_at": datetime.utcnow().isoformat(),
    })

    # Emit message delta (full content in one chunk for simplicity)
    yield create_sse_event("message.delta", {
        "message_id": assistant_msg_id,
        "delta": {"content": response_text},
    })

    # Emit message done
    yield create_sse_event("message.done", {
        "message_id": assistant_msg_id,
        "content": response_text,
    })

    # Store messages in database
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message
    )
    session.add(user_message)

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tool_calls={"data": actions_taken} if actions_taken else None
    )
    session.add(assistant_message)

    # Update conversation
    conversation.updated_at = datetime.utcnow()
    if not conversation.title:
        conversation.title = message[:50] + ("..." if len(message) > 50 else "")
    session.add(conversation)

    session.commit()

    # Emit stream end
    yield create_sse_event("done", {
        "thread_id": thread_id,
    })


@router.post("")
async def chatkit_endpoint(
    request: ChatKitRequest,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """
    ChatKit SSE streaming endpoint.

    Accepts messages and returns SSE stream with:
    - Thread management events
    - Message creation events
    - Tool call events
    - Response content deltas
    - Completion signals

    Compatible with OpenAI ChatKit frontend component.

    Args:
        request: ChatKit message request
        user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        SSE StreamingResponse with NDJSON events
    """
    # Get or generate thread ID
    thread_id = request.thread_id or str(uuid.uuid4())

    return StreamingResponse(
        stream_chat_response(
            message=request.message,
            thread_id=thread_id,
            user_id=user_id,
            session=session,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Thread-Id": thread_id,
        }
    )


@router.get("/threads")
async def list_threads(
    limit: int = 20,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> dict:
    """
    List conversation threads for ChatKit.

    Returns threads with metadata for sidebar display.
    """
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    threads = []
    for conv in conversations:
        msg_count = len(session.exec(
            select(Message).where(Message.conversation_id == conv.id)
        ).all())
        threads.append({
            "thread_id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "message_count": msg_count,
        })

    total = len(session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).all())

    return {
        "threads": threads,
        "total": total,
        "has_more": total > offset + limit,
    }


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> dict:
    """
    Get a specific thread with messages for ChatKit.

    Returns thread metadata and message history.
    """
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == thread_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        return {"error": "Thread not found", "thread_id": thread_id}

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == thread_id)
        .order_by(Message.created_at)
    ).all()

    return {
        "thread_id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "message_id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
    }


@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> dict:
    """Delete a conversation thread."""
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == thread_id,
            Conversation.user_id == user_id
        )
    ).first()

    if not conversation:
        return {"deleted": False, "error": "Thread not found"}

    # Delete messages first
    messages = session.exec(
        select(Message).where(Message.conversation_id == thread_id)
    ).all()
    for msg in messages:
        session.delete(msg)

    session.delete(conversation)
    session.commit()

    return {
        "deleted": True,
        "thread_id": thread_id,
        "messages_deleted": len(messages),
    }
