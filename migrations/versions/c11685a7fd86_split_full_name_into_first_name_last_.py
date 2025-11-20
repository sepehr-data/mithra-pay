"""split full_name into first_name last_name

Revision ID: c11685a7fd86
Revises:
Create Date: 2025-11-19 13:18:44.137320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c11685a7fd86'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1) add new columns
    op.add_column("users", sa.Column("first_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=255), nullable=True))

    # 2) copy data from full_name to first_name (simple version: everything goes to first_name)
    # This is generic SQL; if your DB is Postgres, you could split on space, but keep it simple:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE users SET first_name = full_name WHERE full_name IS NOT NULL"
        )
    )

    # 3) drop the old column
    op.drop_column("users", "full_name")


def downgrade():
    # 1) re-create full_name column
    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))

    # 2) merge first_name + last_name back if you want (simple: just use first_name)
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE users SET full_name = COALESCE(first_name, '')"
        )
    )

    # 3) drop new columns
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
