"""refactor duration_types & subscription_types to static format and use id FKs

Revision ID: a1b2c3d4e5f6
Revises: 4f9a8b2c1d0e
Create Date: 2026-02-03 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "4f9a8b2c1d0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------
    # 0) Drop old FKs / indexes on products (created by previous migration)
    # -------------------------
    op.drop_constraint("fk_products_subscription_types", "products", type_="foreignkey")
    op.drop_constraint("fk_products_duration_types", "products", type_="foreignkey")
    op.drop_index("ix_products_subscription_type", table_name="products")

    # -------------------------
    # 1) Create new static-format tables (v2)
    # -------------------------
    op.create_table(
        "duration_types_v2",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("slug", name="uq_duration_types_slug"),
    )

    op.create_table(
        "subscription_types_v2",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("slug", name="uq_subscription_types_slug"),
    )

    # -------------------------
    # 2) Insert hardcoded rows into v2 tables
    # IMPORTANT: slug را دقیقاً برابر code قبلی گذاشتیم تا مهاجرت داده راحت شود
    # -------------------------
    op.execute(sa.text("""
        INSERT INTO duration_types_v2 (title, slug, description, is_active)
        VALUES
        ('1 ماهه', '1_month', NULL, 1),
        ('3 ماهه', '3_month', NULL, 1),
        ('6 ماهه', '6_month', NULL, 1),
        ('یک ساله', '1_year', NULL, 1)
    """))

    op.execute(sa.text("""
        INSERT INTO subscription_types_v2 (title, slug, description, is_active)
        VALUES
        ('خانوادگی', 'family', NULL, 1),
        ('شخصی', 'individual', NULL, 1)
    """))

    # -------------------------
    # 3) Add new FK columns to products (id-based)
    # -------------------------
    op.add_column("products", sa.Column("duration_type_id", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("subscription_type_id", sa.Integer(), nullable=True))

    op.create_index("ix_products_duration_type_id", "products", ["duration_type_id"], unique=False)
    op.create_index("ix_products_subscription_type_id", "products", ["subscription_type_id"], unique=False)

    # -------------------------
    # 4) Backfill products.*_id from old string columns (duration, subscription_type)
    # duration: products.duration == duration_types.code  -> duration_types_v2.slug -> duration_types_v2.id
    # subscription: products.subscription_type == subscription_types.code -> subscription_types_v2.slug -> subscription_types_v2.id
    # -------------------------
    # duration_type_id
    op.execute(sa.text("""
        UPDATE products p
        JOIN duration_types dt ON dt.code = p.duration
        JOIN duration_types_v2 dt2 ON dt2.slug = dt.code
        SET p.duration_type_id = dt2.id
        WHERE p.duration IS NOT NULL
    """))

    # subscription_type_id
    op.execute(sa.text("""
        UPDATE products p
        JOIN subscription_types st ON st.code = p.subscription_type
        JOIN subscription_types_v2 st2 ON st2.slug = st.code
        SET p.subscription_type_id = st2.id
        WHERE p.subscription_type IS NOT NULL
    """))

    # -------------------------
    # 5) Replace old tables with v2 tables (rename)
    # -------------------------
    op.drop_table("duration_types")
    op.drop_table("subscription_types")

    op.rename_table("duration_types_v2", "duration_types")
    op.rename_table("subscription_types_v2", "subscription_types")

    # -------------------------
    # 6) Create NEW FKs to id
    # -------------------------
    op.create_foreign_key(
        "fk_products_duration_type_id",
        "products",
        "duration_types",
        ["duration_type_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )

    op.create_foreign_key(
        "fk_products_subscription_type_id",
        "products",
        "subscription_types",
        ["subscription_type_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    # downgrade (تقریبی) — برمی‌گردونه به ساختار قبلی code-based
    op.drop_constraint("fk_products_subscription_type_id", "products", type_="foreignkey")
    op.drop_constraint("fk_products_duration_type_id", "products", type_="foreignkey")

    op.drop_index("ix_products_subscription_type_id", table_name="products")
    op.drop_index("ix_products_duration_type_id", table_name="products")

    op.drop_column("products", "subscription_type_id")
    op.drop_column("products", "duration_type_id")

    # recreate old tables
    op.create_table(
        "duration_types_old",
        sa.Column("code", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
    )

    op.create_table(
        "subscription_types_old",
        sa.Column("code", sa.String(50), primary_key=True),
        sa.Column("title", sa.String(50), nullable=False),
    )

    # fill old tables from new tables (slug->code)
    op.execute(sa.text("""
        INSERT INTO duration_types_old (code, title)
        SELECT slug, title FROM duration_types
    """))

    op.execute(sa.text("""
        INSERT INTO subscription_types_old (code, title)
        SELECT slug, title FROM subscription_types
    """))

    # drop new tables and rename old
    op.drop_table("duration_types")
    op.drop_table("subscription_types")

    op.rename_table("duration_types_old", "duration_types")
    op.rename_table("subscription_types_old", "subscription_types")

