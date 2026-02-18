"""create product plan m2m tables

Revision ID: 6779e84c9db1
Revises: b3b483280681
Create Date: 2026-02-08 18:26:22.205643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6779e84c9db1'
down_revision: Union[str, Sequence[str], None] = 'b3b483280681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- Product <-> SubscriptionType (M2M) ---
    op.create_table(
        "product_subscription_types",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("subscription_type_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("product_id", "subscription_type_id"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_type_id"],
            ["subscription_types.id"],
            ondelete="CASCADE",
        ),
    )

    # --- Product <-> DurationType (M2M) ---
    op.create_table(
        "product_duration_types",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("duration_type_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("product_id", "duration_type_id"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["duration_type_id"],
            ["duration_types.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("product_duration_types")
    op.drop_table("product_subscription_types")
