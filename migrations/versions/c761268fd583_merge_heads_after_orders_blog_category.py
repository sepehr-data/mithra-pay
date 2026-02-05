"""merge heads after orders+blog_category

Revision ID: c761268fd583
Revises: 1c2f3a4b5d6e, <NEW_REVISION_ID>
Create Date: 2026-02-02 09:55:28.738362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c761268fd583'
down_revision: Union[str, Sequence[str], None] = ('1c2f3a4b5d6e', '<NEW_REVISION_ID>')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
