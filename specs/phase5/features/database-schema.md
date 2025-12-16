# Phase V: Database Schema Updates

## Overview

Schema changes required to support advanced features in Phase V.

## Current Schema (Phase I-IV)

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Phase V Schema Additions

### 1. Tasks Table - New Columns

```sql
-- Add due date
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE NULL;

-- Add reminder time
ALTER TABLE tasks ADD COLUMN remind_at TIMESTAMP WITH TIME ZONE NULL;

-- Add priority (1=High, 2=Medium, 3=Low)
ALTER TABLE tasks ADD COLUMN priority INTEGER CHECK (priority IN (1, 2, 3));

-- Add recurrence rule (iCal RRULE format)
ALTER TABLE tasks ADD COLUMN recurrence_rule VARCHAR(255) NULL;

-- Add recurrence end date
ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE NULL;

-- Add parent task reference (for recurring task instances)
ALTER TABLE tasks ADD COLUMN parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL;

-- Add full-text search index
CREATE INDEX tasks_title_search_idx ON tasks USING GIN (to_tsvector('english', title));

-- Add index for filtering by due date
CREATE INDEX tasks_due_date_idx ON tasks(user_id, due_date) WHERE due_date IS NOT NULL;

-- Add index for filtering by priority
CREATE INDEX tasks_priority_idx ON tasks(user_id, priority) WHERE priority IS NOT NULL;
```

### 2. Tags Table (New)

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',  -- Hex color code
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT tags_name_user_unique UNIQUE(name, user_id)
);

-- Index for user's tags
CREATE INDEX tags_user_id_idx ON tags(user_id);
```

### 3. Task Tags Junction Table (New)

```sql
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

-- Index for finding tasks by tag
CREATE INDEX task_tags_tag_id_idx ON task_tags(tag_id);
```

### 4. Task Events Table (New - Audit Log)

```sql
CREATE TABLE task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    user_id VARCHAR NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'created', 'updated', 'completed', 'deleted'
    event_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for querying events by task
CREATE INDEX task_events_task_id_idx ON task_events(task_id);

-- Index for querying events by user
CREATE INDEX task_events_user_id_idx ON task_events(user_id, created_at DESC);
```

---

## Complete Phase V Tasks Schema

```sql
CREATE TABLE tasks (
    -- Core fields (Phase I)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Phase V: Due dates & Reminders
    due_date TIMESTAMP WITH TIME ZONE NULL,
    remind_at TIMESTAMP WITH TIME ZONE NULL,

    -- Phase V: Priority
    priority INTEGER CHECK (priority IN (1, 2, 3)),  -- 1=High, 2=Medium, 3=Low

    -- Phase V: Recurring tasks
    recurrence_rule VARCHAR(255) NULL,  -- iCal RRULE format
    recurrence_end_date TIMESTAMP WITH TIME ZONE NULL,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX tasks_user_id_idx ON tasks(user_id);
CREATE INDEX tasks_due_date_idx ON tasks(user_id, due_date) WHERE due_date IS NOT NULL;
CREATE INDEX tasks_priority_idx ON tasks(user_id, priority) WHERE priority IS NOT NULL;
CREATE INDEX tasks_title_search_idx ON tasks USING GIN (to_tsvector('english', title));
CREATE INDEX tasks_remind_at_idx ON tasks(remind_at) WHERE remind_at IS NOT NULL;
```

---

## SQLModel Updates

### Task Model
```python
# backend/app/models/task.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Core fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    completed: bool = Field(default=False)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase V fields
    due_date: Optional[datetime] = Field(default=None)
    remind_at: Optional[datetime] = Field(default=None)
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    recurrence_rule: Optional[str] = Field(default=None, max_length=255)
    recurrence_end_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")

    # Relationships
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
```

### Tag Model
```python
# backend/app/models/tag.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50)
    color: str = Field(default="#6B7280", max_length=7)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="tags", link_model="TaskTag")

class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### TaskEvent Model
```python
# backend/app/models/task_event.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

class TaskEvent(SQLModel, table=True):
    __tablename__ = "task_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(index=True)
    user_id: str = Field(index=True)
    event_type: str = Field(max_length=50)  # created, updated, completed, deleted
    event_data: dict[str, Any] = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Migration Strategy

### Alembic Migration Script
```python
# alembic/versions/xxx_phase5_schema.py
"""Phase V schema updates

Revision ID: phase5_schema
Revises: previous_revision
Create Date: 2025-12-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Add columns to tasks
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True)))
    op.add_column('tasks', sa.Column('remind_at', sa.DateTime(timezone=True)))
    op.add_column('tasks', sa.Column('priority', sa.Integer()))
    op.add_column('tasks', sa.Column('recurrence_rule', sa.String(255)))
    op.add_column('tasks', sa.Column('recurrence_end_date', sa.DateTime(timezone=True)))
    op.add_column('tasks', sa.Column('parent_task_id', postgresql.UUID()))

    # Add check constraint for priority
    op.create_check_constraint('tasks_priority_check', 'tasks', 'priority IN (1, 2, 3)')

    # Add foreign key for parent_task_id
    op.create_foreign_key('tasks_parent_task_id_fkey', 'tasks', 'tasks', ['parent_task_id'], ['id'], ondelete='SET NULL')

    # Create indexes
    op.create_index('tasks_due_date_idx', 'tasks', ['user_id', 'due_date'])
    op.create_index('tasks_priority_idx', 'tasks', ['user_id', 'priority'])
    op.create_index('tasks_title_search_idx', 'tasks', [sa.text("to_tsvector('english', title)")], postgresql_using='gin')

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), server_default='#6B7280'),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('name', 'user_id', name='tags_name_user_unique')
    )
    op.create_index('tags_user_id_idx', 'tags', ['user_id'])

    # Create task_tags junction table
    op.create_table(
        'task_tags',
        sa.Column('task_id', postgresql.UUID(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', postgresql.UUID(), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('task_tags_tag_id_idx', 'task_tags', ['tag_id'])

    # Create task_events table
    op.create_table(
        'task_events',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('task_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_data', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('task_events_task_id_idx', 'task_events', ['task_id'])
    op.create_index('task_events_user_id_idx', 'task_events', ['user_id', 'created_at'])

def downgrade():
    # Drop task_events
    op.drop_table('task_events')

    # Drop task_tags
    op.drop_table('task_tags')

    # Drop tags
    op.drop_table('tags')

    # Drop indexes
    op.drop_index('tasks_title_search_idx')
    op.drop_index('tasks_priority_idx')
    op.drop_index('tasks_due_date_idx')

    # Drop columns
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence_rule')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'remind_at')
    op.drop_column('tasks', 'due_date')
```

---

## Data Types Reference

### Priority Values
| Value | Meaning |
|-------|---------|
| 1 | High |
| 2 | Medium |
| 3 | Low |
| NULL | No priority |

### Event Types
| Type | Description |
|------|-------------|
| `created` | Task was created |
| `updated` | Task was modified |
| `completed` | Task was marked complete |
| `uncompleted` | Task was marked incomplete |
| `deleted` | Task was deleted |

### Recurrence Rules (RRULE)
| Pattern | RRULE |
|---------|-------|
| Daily | `FREQ=DAILY` |
| Weekdays | `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` |
| Weekly (Mon) | `FREQ=WEEKLY;BYDAY=MO` |
| Monthly (1st) | `FREQ=MONTHLY;BYMONTHDAY=1` |
| Monthly (last Fri) | `FREQ=MONTHLY;BYDAY=-1FR` |

---

## Acceptance Criteria

- [ ] All migrations run successfully on Neon DB
- [ ] Existing tasks preserved (no data loss)
- [ ] New columns nullable to support existing data
- [ ] Indexes improve query performance
- [ ] Full-text search works for titles
- [ ] Foreign key constraints work correctly
