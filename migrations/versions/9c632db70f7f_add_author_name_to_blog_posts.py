"""add author_name to blog_posts

Revision ID: 9c632db70f7f
Revises: c11685a7fd86
Create Date: 2026-01-20 10:58:35.510042

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c632db70f7f'
down_revision: Union[str, Sequence[str], None] = 'c11685a7fd86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'blog_posts',
        sa.Column('author_name', sa.String(255), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('blog_posts', 'author_name')

