"""add duration_types + subscription_types and link to products

Revision ID: 4f9a8b2c1d0e
Revises: c761268fd583
Create Date: 2026-02-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4f9a8b2c1d0e"
down_revision: Union[str, None] = "c761268fd583"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) duration_types (hardcoded)
    op.create_table(
        "duration_types",
        sa.Column("code", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
    )

    op.execute(sa.text("""
        INSERT INTO duration_types (code, title) VALUES
        ('1_month', '1 ماهه'),
        ('3_month', '3 ماهه'),
        ('6_month', '6 ماهه'),
        ('1_year',  'یک ساله')
    """))

    # 2) subscription_types (hardcoded)
    op.create_table(
        "subscription_types",
        sa.Column("code", sa.String(50), primary_key=True),   # family | individual
        sa.Column("title", sa.String(50), nullable=False),    # خانوادگی | شخصی
    )

    op.execute(sa.text("""
        INSERT INTO subscription_types (code, title) VALUES
        ('family', 'خانوادگی'),
        ('individual', 'شخصی')
    """))

    # 3) add columns to products
    # subscription_type -> FK to subscription_types.code
    op.add_column(
        "products",
        sa.Column("subscription_type", sa.String(50), nullable=True),
    )
    op.create_index(
        "ix_products_subscription_type",
        "products",
        ["subscription_type"],
        unique=False,
    )

    # personal_account boolean
    op.add_column(
        "products",
        sa.Column("personal_account", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )

    # 4) FK: products.duration -> duration_types.code
    op.create_foreign_key(
        "fk_products_duration_types",
        "products",
        "duration_types",
        ["duration"],
        ["code"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )

    # 5) FK: products.subscription_type -> subscription_types.code
    op.create_foreign_key(
        "fk_products_subscription_types",
        "products",
        "subscription_types",
        ["subscription_type"],
        ["code"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    # drop FKs
    op.drop_constraint("fk_products_subscription_types", "products", type_="foreignkey")
    op.drop_constraint("fk_products_duration_types", "products", type_="foreignkey")

    # drop indexes
    op.drop_index("ix_products_subscription_type", table_name="products")

    # drop columns
    op.drop_column("products", "personal_account")
    op.drop_column("products", "subscription_type")

    # drop tables
    op.drop_table("subscription_types")
    op.drop_table("duration_types")
