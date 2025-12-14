from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # user, assistant, system, tool
    content: str = Field(default="")
    tool_calls: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    metadata_: Optional[dict[str, Any]] = Field(default=None, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
