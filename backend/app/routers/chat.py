"""
Chat API Endpoint

Handles conversation with the AI agent, including:
- Message processing
- Conversation history management
- Tool execution via MCP

Flow: fetch history → build messages → run agent → store messages → return response
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

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
    DeleteHistoryResponse,
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

    # 3. Build messages for agent (OpenAI format)
    # Note: We only pass user and assistant messages, not tool calls
    # The agent will re-execute tools if needed based on conversation context
    messages = []
    for msg in history:
        if msg.role in ("user", "assistant"):
            messages.append({"role": msg.role, "content": msg.content})

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
        tool_calls={"data": actions_taken} if actions_taken else None
    )
    session.add(assistant_message)

    # Update conversation timestamp and title
    conversation.updated_at = datetime.utcnow()
    if not conversation.title:
        # Auto-generate title from first user message
        conversation.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
    session.add(conversation)

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

    # Build response with message counts
    conv_responses = []
    for conv in conversations:
        msg_count = len(session.exec(
            select(Message).where(Message.conversation_id == conv.id)
        ).all())
        conv_responses.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count
            )
        )

    # Get messages if specific conversation requested
    messages = []
    if conversation_id:
        # Verify conversation belongs to user
        conv_check = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        if conv_check:
            msg_query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            messages = [
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    tool_calls=m.tool_calls,
                    created_at=m.created_at
                )
                for m in session.exec(msg_query).all()
            ]

    # Count total conversations for pagination
    total = len(session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).all())

    return HistoryResponse(
        conversations=conv_responses,
        messages=messages,
        total=total,
        has_more=total > offset + limit
    )


@router.delete("/history", response_model=DeleteHistoryResponse)
async def clear_history(
    conversation_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> DeleteHistoryResponse:
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

        # Delete messages first
        messages = session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        for msg in messages:
            session.delete(msg)

        session.delete(conversation)
        session.commit()

        return DeleteHistoryResponse(
            deleted=True,
            conversations_deleted=1,
            messages_deleted=len(messages)
        )
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

        return DeleteHistoryResponse(
            deleted=True,
            conversations_deleted=len(conversations),
            messages_deleted=total_messages
        )
