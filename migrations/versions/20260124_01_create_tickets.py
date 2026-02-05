"""create tickets table

Revision ID: 20260124_01_create_tickets
Revises:
Create Date: 2026-01-24 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260124_01_create_tickets'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(50), nullable=False),
        sa.Column('order_number', sa.String(100), nullable=True),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='OPEN'),
        sa.Column('accepted_policy', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
    )


def downgrade():
    op.drop_table('tickets')
