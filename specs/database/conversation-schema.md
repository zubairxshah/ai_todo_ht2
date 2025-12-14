# Database Schema: Conversations

> Schema for storing chat conversations and messages with user isolation

## Overview

The conversation system stores chat history between users and the AI assistant. Each conversation belongs to a single user, and messages are stored chronologically within conversations.

## Entity Relationship

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │   Conversation   │       │   Message    │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │──────<│ id (PK)          │──────<│ id (PK)      │
│ email        │       │ user_id (FK)     │       │ conv_id (FK) │
│ name         │       │ title            │       │ role         │
│ ...          │       │ created_at       │       │ content      │
└──────────────┘       │ updated_at       │       │ tool_calls   │
                       └──────────────────┘       │ created_at   │
                                                  └──────────────┘
```

## Tables

### conversation

Stores conversation sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique conversation ID |
| `user_id` | VARCHAR(255) | NOT NULL, INDEX | Owner's user ID (from Better Auth) |
| `title` | VARCHAR(255) | NULL | Auto-generated or user-set title |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last activity timestamp |

**Indexes:**
- `idx_conversation_user_id` on `user_id`
- `idx_conversation_updated_at` on `updated_at DESC`

### message

Stores individual messages within conversations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique message ID |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY | Parent conversation |
| `role` | VARCHAR(20) | NOT NULL | Message role: 'user', 'assistant', 'system', 'tool' |
| `content` | TEXT | NOT NULL | Message content |
| `tool_calls` | JSONB | NULL | Tool invocations (for assistant messages) |
| `tool_call_id` | VARCHAR(255) | NULL | Tool call ID (for tool result messages) |
| `metadata` | JSONB | NULL | Additional metadata (tokens, timing, etc.) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes:**
- `idx_message_conversation_id` on `conversation_id`
- `idx_message_created_at` on `created_at`

**Foreign Keys:**
- `conversation_id` REFERENCES `conversation(id)` ON DELETE CASCADE

## SQLModel Definitions

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid


class Conversation(SQLModel, table=True):
    """Chat conversation session."""

    __tablename__ = "conversation"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique conversation ID"
    )
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Owner's user ID from Better Auth"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Conversation title (auto-generated or user-set)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, Any
import uuid


class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "message"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique message ID"
    )
    conversation_id: str = Field(
        foreign_key="conversation.id",
        nullable=False,
        index=True
    )
    role: str = Field(
        nullable=False,
        description="Message role: user, assistant, system, tool"
    )
    content: str = Field(
        nullable=False,
        description="Message content"
    )
    tool_calls: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Tool invocations for assistant messages"
    )
    tool_call_id: Optional[str] = Field(
        default=None,
        description="Tool call ID for tool result messages"
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

## Pydantic Schemas

### Request/Response Schemas

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str
    conversation_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema for message in responses."""
    id: str
    role: str
    content: str
    tool_calls: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation in responses."""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Conversation with full message history."""
    messages: List[MessageResponse]


class ChatRequest(BaseModel):
    """Schema for chat endpoint request."""
    message: str
    conversation_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Schema for chat endpoint response."""
    response: str
    conversation_id: str
    actions_taken: List[dict[str, Any]] = []
    metadata: Optional[dict[str, Any]] = None
```

## SQL Migrations

### Create Tables

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversation table
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for conversation
CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_updated_at ON conversation(updated_at DESC);

-- Create message table
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_call_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for message
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);

-- Update trigger for conversation.updated_at
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation SET updated_at = NOW() WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON message
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

### Drop Tables

```sql
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON message;
DROP FUNCTION IF EXISTS update_conversation_timestamp();
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS conversation;
```

## Query Patterns

### Get User's Conversations

```sql
SELECT
    c.id,
    c.title,
    c.created_at,
    c.updated_at,
    COUNT(m.id) as message_count
FROM conversation c
LEFT JOIN message m ON m.conversation_id = c.id
WHERE c.user_id = :user_id
GROUP BY c.id
ORDER BY c.updated_at DESC
LIMIT :limit OFFSET :offset;
```

### Get Conversation with Messages

```sql
SELECT
    m.id,
    m.role,
    m.content,
    m.tool_calls,
    m.created_at
FROM message m
WHERE m.conversation_id = :conversation_id
ORDER BY m.created_at ASC;
```

### Auto-Generate Conversation Title

```sql
-- Take first user message, truncate to 50 chars
UPDATE conversation
SET title = LEFT(
    (SELECT content FROM message
     WHERE conversation_id = :conv_id AND role = 'user'
     ORDER BY created_at ASC LIMIT 1),
    50
)
WHERE id = :conv_id AND title IS NULL;
```

## Security Considerations

1. **User Isolation**: All queries must include `WHERE user_id = :user_id`
2. **Cascade Delete**: Deleting a conversation removes all messages
3. **No Cross-User Access**: Foreign key doesn't enforce this; application must
4. **Sensitive Data**: Message content may contain sensitive info; handle carefully
5. **Retention Policy**: Consider implementing message retention/purge policies
