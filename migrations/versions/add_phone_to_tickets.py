"""add phone column to tickets table

Revision ID: 3f2a1c9b7e4d
Revises: a1b2c3d4e5f6
Create Date: 2026-01-26 12:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "3f2a1c9b7e4d"
down_revision = "95eccc8783c4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tickets",
        sa.Column("phone", sa.String(length=255), nullable=False)
    )


def downgrade():
    op.drop_column("tickets", "phone")
