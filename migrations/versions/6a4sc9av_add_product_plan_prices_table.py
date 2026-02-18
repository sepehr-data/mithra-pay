"""add product_plan_prices + ensure order_items FKs safely

Revision ID: 8c4f2a1d9e30
Revises: db77bb5bdf8a
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "8c4f2a1d9e30"
down_revision: Union[str, Sequence[str], None] = "db77bb5bdf8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    return table_name in insp.get_table_names()


def _has_column(table_name: str, col_name: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return col_name in cols


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    idxs = insp.get_indexes(table_name) or []
    return any(i.get("name") == index_name for i in idxs)


def _fk_exists(
    source_table: str,
    constrained_columns: list[str],
    referred_table: str,
    referred_columns: list[str],
) -> bool:
    """
    checks existence of FK by structure, not by name (because existing FKs might have auto names)
    """
    bind = op.get_bind()
    insp = inspect(bind)
    fks = insp.get_foreign_keys(source_table) or []

    for fk in fks:
        if (fk.get("constrained_columns") or []) == constrained_columns and \
           (fk.get("referred_table") or "") == referred_table and \
           (fk.get("referred_columns") or []) == referred_columns:
            return True
    return False


def _ensure_fk(
    *,
    name: str,
    source_table: str,
    referent_table: str,
    local_cols: list[str],
    remote_cols: list[str],
    ondelete: str | None = None,
) -> None:
    # if FK already exists (even with auto-generated name), do nothing
    if _fk_exists(source_table, local_cols, referent_table, remote_cols):
        return

    op.create_foreign_key(
        name,
        source_table,
        referent_table,
        local_cols,
        remote_cols,
        ondelete=ondelete,
    )


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1) order_items: keep safe checks, but ALSO ensure FKs exist
    # ---------------------------------------------------------
    if _has_table("order_items"):
        # columns (safe, in case some env missed them)
        if not _has_column("order_items", "duration_type_id"):
            op.add_column("order_items", sa.Column("duration_type_id", sa.Integer(), nullable=True))

        if not _has_column("order_items", "subscription_type_id"):
            op.add_column("order_items", sa.Column("subscription_type_id", sa.Integer(), nullable=True))

        if not _has_column("order_items", "personal_account"):
            # safe for existing rows
            op.add_column("order_items", sa.Column("personal_account", sa.Boolean(), nullable=True))
            op.execute(sa.text("UPDATE order_items SET personal_account = 0 WHERE personal_account IS NULL"))
            op.alter_column("order_items", "personal_account", existing_type=sa.Boolean(), nullable=False)
        else:
            # if exists but has NULLs (edge case), fix
            op.execute(sa.text("UPDATE order_items SET personal_account = 0 WHERE personal_account IS NULL"))
            try:
                op.alter_column("order_items", "personal_account", existing_type=sa.Boolean(), nullable=False)
            except Exception:
                pass

        # ensure FKs exist (even if old migration created them with auto-name or failed)
        if _has_column("order_items", "subscription_type_id"):
            _ensure_fk(
                name="fk_order_items_subscription_type_id",
                source_table="order_items",
                referent_table="subscription_types",
                local_cols=["subscription_type_id"],
                remote_cols=["id"],
                ondelete=None,
            )

        if _has_column("order_items", "duration_type_id"):
            _ensure_fk(
                name="fk_order_items_duration_type_id",
                source_table="order_items",
                referent_table="duration_types",
                local_cols=["duration_type_id"],
                remote_cols=["id"],
                ondelete=None,
            )

    # ---------------------------------------------------------
    # 2) product_plan_prices table
    # ---------------------------------------------------------
    if not _has_table("product_plan_prices"):
        op.create_table(
            "product_plan_prices",
            sa.Column("id", sa.Integer(), primary_key=True),

            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("subscription_type_id", sa.Integer(), nullable=False),
            sa.Column("duration_type_id", sa.Integer(), nullable=False),

            sa.Column("price", sa.Numeric(10, 2), nullable=False),

            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),

            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["subscription_type_id"], ["subscription_types.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["duration_type_id"], ["duration_types.id"], ondelete="CASCADE"),

            sa.UniqueConstraint(
                "product_id", "subscription_type_id", "duration_type_id",
                name="uq_product_plan_price",
            ),
        )

    # indexes (safe)
    if _has_table("product_plan_prices"):
        if not _has_index("product_plan_prices", "ix_product_plan_prices_product_id"):
            op.create_index("ix_product_plan_prices_product_id", "product_plan_prices", ["product_id"])
        if not _has_index("product_plan_prices", "ix_product_plan_prices_subscription_type_id"):
            op.create_index("ix_product_plan_prices_subscription_type_id", "product_plan_prices", ["subscription_type_id"])
        if not _has_index("product_plan_prices", "ix_product_plan_prices_duration_type_id"):
            op.create_index("ix_product_plan_prices_duration_type_id", "product_plan_prices", ["duration_type_id"])


def downgrade() -> None:
    # product_plan_prices rollback
    if _has_table("product_plan_prices"):
        if _has_index("product_plan_prices", "ix_product_plan_prices_duration_type_id"):
            op.drop_index("ix_product_plan_prices_duration_type_id", table_name="product_plan_prices")
        if _has_index("product_plan_prices", "ix_product_plan_prices_subscription_type_id"):
            op.drop_index("ix_product_plan_prices_subscription_type_id", table_name="product_plan_prices")
        if _has_index("product_plan_prices", "ix_product_plan_prices_product_id"):
            op.drop_index("ix_product_plan_prices_product_id", table_name="product_plan_prices")
        op.drop_table("product_plan_prices")

    # order_items: only drop the named FKs we created (if present)
    if _has_table("order_items"):
        for fk_name in ("fk_order_items_subscription_type_id", "fk_order_items_duration_type_id"):
            try:
                op.drop_constraint(fk_name, "order_items", type_="foreignkey")
            except Exception:
                pass

        # (اختیاری) ستون‌ها رو هم می‌تونی نگه داری؛ ولی اگر خواستی برداری:
        # for col in ("personal_account", "subscription_type_id", "duration_type_id"):
        #     if _has_column("order_items", col):
        #         op.drop_column("order_items", col)
