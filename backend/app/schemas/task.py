from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=500)
    # Phase V fields
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[int] = Field(default=None, ge=1, le=3)  # 1=High, 2=Medium, 3=Low
    recurrence_rule: Optional[str] = Field(default=None, max_length=255)  # iCal RRULE
    recurrence_end_date: Optional[datetime] = None
    tag_ids: Optional[list[str]] = None  # List of tag IDs to attach


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    # Phase V fields
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    recurrence_rule: Optional[str] = Field(default=None, max_length=255)
    recurrence_end_date: Optional[datetime] = None
    tag_ids: Optional[list[str]] = None  # Replace all tags


class TagResponse(BaseModel):
    """Schema for tag in response."""
    id: str
    name: str
    color: str

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Schema for task in response."""
    id: str
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    # Phase V fields
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[int] = None
    recurrence_rule: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    parent_task_id: Optional[str] = None
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list."""
    tasks: list[TaskResponse]
    total: int
    page: int
    per_page: int


class TaskFilterParams(BaseModel):
    """Query parameters for filtering tasks."""
    status: Optional[str] = None  # "all", "completed", "pending"
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    tag_id: Optional[str] = None
    search: Optional[str] = None
    overdue: Optional[bool] = None
    sort_by: Optional[str] = "created_at"  # "due_date", "priority", "title", "created_at"
    sort_order: Optional[str] = "desc"  # "asc" or "desc"
    page: int = 1
    per_page: int = 50
