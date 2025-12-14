from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(min_length=1, max_length=500)
    completed: bool = Field(default=False)
    user_id: str = Field(index=True)  # No FK - users managed by Better Auth on frontend
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
