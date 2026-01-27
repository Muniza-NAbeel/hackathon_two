"""Create Dapr state table for PostgreSQL state store

Revision ID: phase5_dapr_state
Revises: phase5_reminder_fields
Create Date: 2026-01-18 10:05:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'phase5_dapr_state'
down_revision = 'phase5_reminder_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create Dapr state table for PostgreSQL state store component.

    This table is used by Dapr for:
    - Idempotency tracking (storing processed event IDs)
    - Service state management

    Schema follows Dapr PostgreSQL state store requirements.
    """
    op.create_table(
        'dapr_state',
        sa.Column('key', sa.String(255), primary_key=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), default=1, nullable=False),
        sa.Column('insert_date', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('update_date', sa.DateTime(), onupdate=sa.func.now(), nullable=True),
        sa.Column('expiration_time', sa.DateTime(), nullable=True),
    )

    # Index for TTL-based cleanup
    op.create_index(
        'ix_dapr_state_expiration',
        'dapr_state',
        ['expiration_time'],
        postgresql_where=sa.text('expiration_time IS NOT NULL')
    )


def downgrade() -> None:
    """Remove Dapr state table"""
    op.drop_index('ix_dapr_state_expiration', 'dapr_state')
    op.drop_table('dapr_state')
