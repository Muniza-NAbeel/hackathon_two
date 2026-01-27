"""Add Phase 5 reminder fields to tasks table

Revision ID: phase5_reminder_fields
Revises: add_advanced_features
Create Date: 2026-01-18 10:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'phase5_reminder_fields'
down_revision = 'add_advanced_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add Phase 5 reminder fields to tasks table:
    - remind_at (datetime, nullable): When to send reminder
    - reminder_sent (boolean, default false): Prevent duplicate reminders
    - Partial index on remind_at where reminder_sent = false
    """
    # Add reminder columns
    op.add_column('tasks', sa.Column('remind_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'))

    # Create partial index for efficient reminder queries
    # Only index tasks that haven't had their reminder sent yet
    op.create_index(
        'ix_tasks_remind_at_pending',
        'tasks',
        ['remind_at'],
        postgresql_where=sa.text('reminder_sent = false')
    )


def downgrade() -> None:
    """Remove Phase 5 reminder fields"""
    op.drop_index('ix_tasks_remind_at_pending', 'tasks')
    op.drop_column('tasks', 'reminder_sent')
    op.drop_column('tasks', 'remind_at')
