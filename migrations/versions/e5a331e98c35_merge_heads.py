"""merge heads

Revision ID: e5a331e98c35
Revises: 20260105_add_user_profile_fields, 9c632db70f7f
Create Date: 2026-01-20 11:29:14.515366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a331e98c35'
down_revision: Union[str, Sequence[str], None] = ('20260105_add_user_profile_fields', '9c632db70f7f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
