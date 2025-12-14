# Database Schema

**Database:** Neon Serverless PostgreSQL
**ORM:** SQLModel (SQLAlchemy + Pydantic)

## Tables

### users

Managed by **Better Auth** - do not modify directly.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | User identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| email_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| name | VARCHAR(255) | NULLABLE | Display name |
| image | TEXT | NULLABLE | Avatar URL |
| created_at | TIMESTAMP | NOT NULL | Account creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Note:** Better Auth manages additional tables for sessions, accounts, and verification tokens. See Better Auth documentation for full schema.

---

### tasks

Application-managed table for user tasks.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Task identifier |
| title | VARCHAR(255) | NOT NULL | Task title/description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| user_id | UUID | NOT NULL, FK → users.id | Owner reference |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification |

**Indexes:**
- `idx_tasks_user_id` on `user_id` - Fast lookup by owner

**Foreign Key:**
- `user_id` → `users.id` ON DELETE CASCADE

---

## SQLModel Definition

```python
# backend/app/models/task.py

from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Relationships

```
┌─────────────┐       ┌─────────────┐
│   users     │       │   tasks     │
├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ user_id (FK)│
│ email       │   1:N │ id (PK)     │
│ ...         │       │ title       │
└─────────────┘       │ completed   │
                      └─────────────┘
```

- One user has many tasks (1:N)
- Deleting a user cascades to delete their tasks

---

## Data Access Patterns

### Always Filter by user_id

```python
# CORRECT - filter by authenticated user
tasks = session.exec(
    select(Task).where(Task.user_id == current_user_id)
).all()

# WRONG - never trust client-provided user_id
tasks = session.exec(
    select(Task).where(Task.user_id == request.user_id)  # NO!
).all()
```

### Ownership Check on Single Task

```python
task = session.get(Task, task_id)
if task is None:
    raise HTTPException(404, "Task not found")
if task.user_id != current_user_id:
    raise HTTPException(403, "Not authorized")
```

---

## Migrations

Using SQLModel's `create_all()` for MVP:

```python
# backend/app/database.py
from sqlmodel import SQLModel, create_engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

For production, consider Alembic for proper migrations.

---

## Environment

```bash
# .env
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

Connection pooling handled by Neon serverless driver.
