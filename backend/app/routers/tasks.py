from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func, or_
from sqlalchemy import desc, asc
from datetime import datetime
from typing import Optional

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.models.task import Task
from app.models.tag import Tag, TaskTag
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TagResponse,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_task_with_tags(task: Task, session: Session) -> TaskResponse:
    """Convert Task model to TaskResponse with tags."""
    # Get tags for this task
    statement = (
        select(Tag)
        .join(TaskTag)
        .where(TaskTag.task_id == task.id)
    )
    tags = session.exec(statement).all()
    tag_responses = [TagResponse(id=t.id, name=t.name, color=t.color) for t in tags]

    return TaskResponse(
        id=task.id,
        title=task.title,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at,
        due_date=task.due_date,
        remind_at=task.remind_at,
        priority=task.priority,
        recurrence_rule=task.recurrence_rule,
        recurrence_end_date=task.recurrence_end_date,
        parent_task_id=task.parent_task_id,
        tags=tag_responses,
    )


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
    # Filter parameters
    status: Optional[str] = Query(None, description="Filter by status: all, completed, pending"),
    priority: Optional[int] = Query(None, ge=1, le=3, description="Filter by priority: 1=High, 2=Medium, 3=Low"),
    tag_id: Optional[str] = Query(None, description="Filter by tag ID"),
    search: Optional[str] = Query(None, description="Search in task title"),
    overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    # Sort parameters
    sort_by: Optional[str] = Query("created_at", description="Sort by: due_date, priority, title, created_at"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
) -> list[TaskResponse]:
    """List all tasks for the current user with optional filtering and sorting."""
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "completed":
        statement = statement.where(Task.completed == True)
    elif status == "pending":
        statement = statement.where(Task.completed == False)

    # Apply priority filter
    if priority is not None:
        statement = statement.where(Task.priority == priority)

    # Apply tag filter
    if tag_id:
        statement = statement.join(TaskTag).where(TaskTag.tag_id == tag_id)

    # Apply search filter
    if search:
        statement = statement.where(Task.title.ilike(f"%{search}%"))

    # Apply overdue filter
    if overdue:
        now = datetime.utcnow()
        statement = statement.where(
            Task.due_date < now,
            Task.completed == False
        )

    # Apply sorting
    sort_column = {
        "due_date": Task.due_date,
        "priority": Task.priority,
        "title": Task.title,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
    }.get(sort_by, Task.created_at)

    if sort_order == "asc":
        statement = statement.order_by(asc(sort_column))
    else:
        statement = statement.order_by(desc(sort_column))

    tasks = session.exec(statement).all()

    # Convert to response with tags
    return [get_task_with_tags(task, session) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Get a single task by ID."""
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task",
        )

    return get_task_with_tags(task, session)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Create a new task for the current user."""
    task = Task(
        title=task_data.title,
        user_id=user_id,
        due_date=task_data.due_date,
        remind_at=task_data.remind_at,
        priority=task_data.priority,
        recurrence_rule=task_data.recurrence_rule,
        recurrence_end_date=task_data.recurrence_end_date,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Attach tags if provided
    if task_data.tag_ids:
        for tag_id in task_data.tag_ids:
            # Verify tag exists and belongs to user
            tag = session.exec(
                select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
            ).first()
            if tag:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)
        session.commit()

    return get_task_with_tags(task, session)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """Update a task. Only the owner can update their tasks."""
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Enforce user ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )

    # Update core fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Update Phase V fields if provided
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.remind_at is not None:
        task.remind_at = task_data.remind_at
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.recurrence_rule is not None:
        task.recurrence_rule = task_data.recurrence_rule
    if task_data.recurrence_end_date is not None:
        task.recurrence_end_date = task_data.recurrence_end_date

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()

    # Update tags if provided
    if task_data.tag_ids is not None:
        # Remove existing tags
        existing_task_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()
        for tt in existing_task_tags:
            session.delete(tt)

        # Add new tags
        for tag_id in task_data.tag_ids:
            tag = session.exec(
                select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
            ).first()
            if tag:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)
        session.commit()

    session.refresh(task)
    return get_task_with_tags(task, session)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> None:
    """Delete a task. Only the owner can delete their tasks."""
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Enforce user ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task",
        )

    # Delete associated task_tags first (cascade should handle this but be explicit)
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    for tt in task_tags:
        session.delete(tt)

    session.delete(task)
    session.commit()
