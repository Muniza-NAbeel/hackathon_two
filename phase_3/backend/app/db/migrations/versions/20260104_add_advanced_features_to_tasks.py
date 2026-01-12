"""Add advanced features to tasks table

Revision ID: add_advanced_features
Revises: cd44220992bd
Create Date: 2026-01-04 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_advanced_features'
down_revision = 'cd44220992bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add advanced features from Phase 1 to tasks table:
    - tags (JSON array for categories)
    - recurrence (str for daily/weekly/monthly patterns)
    - notes (JSON array for task comments)
    - completed (boolean for quick status check)
    - Update priority to support 'urgent' level
    """
    # Add new columns
    op.add_column('tasks', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tasks', sa.Column('recurrence', sa.String(length=50), nullable=False, server_default='none'))
    op.add_column('tasks', sa.Column('notes', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tasks', sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Remove advanced features columns"""
    op.drop_column('tasks', 'completed')
    op.drop_column('tasks', 'notes')
    op.drop_column('tasks', 'recurrence')
    op.drop_column('tasks', 'tags')
