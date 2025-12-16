from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from datetime import datetime

from app.database import get_session
from app.dependencies.auth import get_current_user_id
from app.models.tag import Tag, TaskTag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagWithTaskCount

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagWithTaskCount])
async def list_tags(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> list[TagWithTaskCount]:
    """List all tags for the current user with task counts."""
    # Get all tags for user
    statement = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
    tags = session.exec(statement).all()

    result = []
    for tag in tags:
        # Count tasks for this tag
        count_statement = select(func.count()).where(TaskTag.tag_id == tag.id)
        task_count = session.exec(count_statement).one()

        result.append(TagWithTaskCount(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            created_at=tag.created_at,
            task_count=task_count,
        ))

    return result


@router.get("/{tag_id}", response_model=TagWithTaskCount)
async def get_tag(
    tag_id: str,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> TagWithTaskCount:
    """Get a single tag by ID."""
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this tag",
        )

    # Count tasks for this tag
    count_statement = select(func.count()).where(TaskTag.tag_id == tag.id)
    task_count = session.exec(count_statement).one()

    return TagWithTaskCount(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        task_count=task_count,
    )


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> Tag:
    """Create a new tag for the current user."""
    # Check if tag with same name already exists for this user
    existing = session.exec(
        select(Tag).where(Tag.name == tag_data.name, Tag.user_id == user_id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists",
        )

    tag = Tag(
        name=tag_data.name,
        color=tag_data.color,
        user_id=user_id,
    )
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    tag_data: TagUpdate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> Tag:
    """Update a tag. Only the owner can update their tags."""
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this tag",
        )

    # Check for duplicate name if name is being changed
    if tag_data.name is not None and tag_data.name != tag.name:
        existing = session.exec(
            select(Tag).where(
                Tag.name == tag_data.name,
                Tag.user_id == user_id,
                Tag.id != tag_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists",
            )
        tag.name = tag_data.name

    if tag_data.color is not None:
        tag.color = tag_data.color

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> None:
    """Delete a tag. Only the owner can delete their tags."""
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this tag",
        )

    # Delete associated task_tags first (cascade should handle this but be explicit)
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.tag_id == tag_id)
    ).all()
    for tt in task_tags:
        session.delete(tt)

    session.delete(tag)
    session.commit()
