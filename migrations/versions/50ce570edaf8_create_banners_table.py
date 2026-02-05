"""create banners table

Revision ID: abc123def456
Revises: <previous_revision>
Create Date: 2026-01-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = 'abc123def456'
down_revision = 'e5a331e98c35'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'banners',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('link', sa.String(500), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)
    )

def downgrade():
    op.drop_table('banners')
