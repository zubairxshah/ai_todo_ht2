from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TagCreate(BaseModel):
    """Schema for creating a new tag."""
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#6B7280", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagResponse(BaseModel):
    """Schema for tag in response."""
    id: str
    name: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True


class TagWithTaskCount(TagResponse):
    """Tag response with count of associated tasks."""
    task_count: int = 0
