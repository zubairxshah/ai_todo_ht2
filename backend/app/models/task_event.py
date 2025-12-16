from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Any
import uuid


class TaskEvent(SQLModel, table=True):
    """Audit log for task events - used for event-driven architecture."""
    __tablename__ = "task_events"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(index=True)
    user_id: str = Field(index=True)
    event_type: str = Field(max_length=50)  # created, updated, completed, uncompleted, deleted
    event_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
