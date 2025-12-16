"""phase5_advanced_features

Revision ID: fa6858c90805
Revises:
Create Date: 2025-12-16 20:58:09.545715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fa6858c90805'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase V advanced features."""
    # Create tags table
    op.create_table('tags',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=7), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)
    op.create_index(op.f('ix_tags_user_id'), 'tags', ['user_id'], unique=False)

    # Create task_events audit table
    op.create_table('task_events',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('event_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_events_task_id'), 'task_events', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_events_user_id'), 'task_events', ['user_id'], unique=False)

    # Create task_tags junction table
    op.create_table('task_tags',
        sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tag_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

    # Add Phase V columns to tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('remind_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_rule', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_end_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Add foreign key for parent_task_id (self-referential)
    op.create_foreign_key('fk_tasks_parent_task_id', 'tasks', 'tasks', ['parent_task_id'], ['id'], ondelete='SET NULL')

    # Add indexes for efficient queries
    op.create_index('ix_tasks_due_date', 'tasks', ['user_id', 'due_date'])
    op.create_index('ix_tasks_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('ix_tasks_remind_at', 'tasks', ['remind_at'])


def downgrade() -> None:
    """Downgrade schema - remove Phase V features."""
    # Drop indexes
    op.drop_index('ix_tasks_remind_at', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_due_date', table_name='tasks')

    # Drop foreign key and columns from tasks
    op.drop_constraint('fk_tasks_parent_task_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence_rule')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'remind_at')
    op.drop_column('tasks', 'due_date')

    # Drop junction table
    op.drop_table('task_tags')

    # Drop task_events table
    op.drop_index(op.f('ix_task_events_user_id'), table_name='task_events')
    op.drop_index(op.f('ix_task_events_task_id'), table_name='task_events')
    op.drop_table('task_events')

    # Drop tags table
    op.drop_index(op.f('ix_tags_user_id'), table_name='tags')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
