from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class Tag(SQLModel, table=True):
    """Tag model for categorizing tasks."""
    __tablename__ = "tags"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=50, index=True)
    color: str = Field(default="#6B7280", max_length=7)  # Hex color code
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskTag(SQLModel, table=True):
    """Junction table for many-to-many relationship between tasks and tags."""
    __tablename__ = "task_tags"

    task_id: str = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
