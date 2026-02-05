"""fix orders statuses not null and cleanup empty

Revision ID: <NEW_REVISION_ID>
Revises: aaa7efbc5050
Create Date: <AUTO>

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "<NEW_REVISION_ID>"
down_revision = "aaa7efbc5050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 0) cleanup empty strings (in case some rows have '')
    op.execute("UPDATE orders SET status = NULL WHERE status = ''")
    op.execute("UPDATE orders SET payment_status = NULL WHERE payment_status = ''")
    op.execute("UPDATE orders SET admin_status = 'OPEN' WHERE admin_status = ''")

    # 1) backfill NULLs for existing rows
    op.execute("UPDATE orders SET status = 'PENDING' WHERE status IS NULL")
    op.execute("UPDATE orders SET payment_status = 'UNPAID' WHERE payment_status IS NULL")

    # 2) enforce NOT NULL (with temp server_default to satisfy DB during alter, if needed)
    op.alter_column(
        "orders",
        "status",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default="PENDING",
    )
    op.alter_column(
        "orders",
        "payment_status",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default="UNPAID",
    )

    # 3) remove server_default so future defaults come from app/model logic (same style as your head)
    op.alter_column("orders", "status", server_default=None)
    op.alter_column("orders", "payment_status", server_default=None)


def downgrade() -> None:
    # rollback NOT NULL and defaults
    op.alter_column(
        "orders",
        "status",
        existing_type=sa.String(length=50),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "orders",
        "payment_status",
        existing_type=sa.String(length=50),
        nullable=True,
        server_default=None,
    )
