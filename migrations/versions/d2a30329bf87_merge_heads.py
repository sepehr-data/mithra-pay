"""merge heads

Revision ID: d2a30329bf87
Revises: 20260124_01_create_tickets, abc123def456
Create Date: 2026-01-24 13:41:33.651899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2a30329bf87'
down_revision: Union[str, Sequence[str], None] = ('20260124_01_create_tickets', 'abc123def456')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
