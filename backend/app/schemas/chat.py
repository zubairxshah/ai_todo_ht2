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


class DeleteHistoryResponse(BaseModel):
    """Response schema for DELETE /api/chat/history"""
    deleted: bool
    conversations_deleted: int
    messages_deleted: int
