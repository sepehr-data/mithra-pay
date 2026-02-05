"""add admin_status to orders

Revision ID: aaa7efbc5050
Revises: 3f2a1c9b7e4d
Create Date: 2026-01-27 13:36:33.057356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaa7efbc5050'
down_revision = "3f2a1c9b7e4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) add column with server_default to backfill existing rows
    op.add_column(
        "orders",
        sa.Column("admin_status", sa.String(length=50), nullable=False, server_default="OPEN"),
    )

    # 2) remove server_default so future defaults come from app/model logic
    op.alter_column("orders", "admin_status", server_default=None)


def downgrade() -> None:
    op.drop_column("orders", "admin_status")