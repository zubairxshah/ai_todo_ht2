from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Core fields (Phase I-IV)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(min_length=1, max_length=500)
    completed: bool = Field(default=False)
    user_id: str = Field(index=True)  # No FK - users managed by Better Auth on frontend
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase V: Due dates & Reminders
    due_date: Optional[datetime] = Field(default=None)
    remind_at: Optional[datetime] = Field(default=None)

    # Phase V: Priority (1=High, 2=Medium, 3=Low)
    priority: Optional[int] = Field(default=None, ge=1, le=3)

    # Phase V: Recurring tasks
    recurrence_rule: Optional[str] = Field(default=None, max_length=255)  # iCal RRULE format
    recurrence_end_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[str] = Field(default=None, foreign_key="tasks.id")
