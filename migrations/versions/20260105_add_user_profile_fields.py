"""add user profile fields

Revision ID: 20260105_add_user_profile_fields
Revises: c11685a7fd86
Create Date: 2026-01-05
"""
from typing import Sequence, Union
from alembic import op

revision: str = "20260105_add_user_profile_fields"
down_revision: Union[str, Sequence[str], None] = "c11685a7fd86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users
            ADD COLUMN IF NOT EXISTS national_id VARCHAR(32) NULL,
            ADD COLUMN IF NOT EXISTS bank_number VARCHAR(64) NULL,
            ADD COLUMN IF NOT EXISTS sheba VARCHAR(64) NULL,
            ADD COLUMN IF NOT EXISTS birthday DATE NULL;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
            DROP COLUMN IF EXISTS birthday,
            DROP COLUMN IF EXISTS sheba,
            DROP COLUMN IF EXISTS bank_number,
            DROP COLUMN IF EXISTS national_id;
    """)
