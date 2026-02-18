"""create carts, cart_items, product_subscription_duration_tables

Revision ID: xxxx_add_carts_and_product_plans
Revises: a1b2c3d4e5f6
Create Date: 2026-02-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "xxxx_add_carts_and_product_plans"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    # ========================
    # 1) جدول‌های Cart و CartItem
    # ========================
    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id"), nullable=False, index=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False, index=True),
        sa.Column("title_snapshot", sa.String(length=255)),
        sa.Column("unit_price", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("line_total", sa.DECIMAL(10, 2), nullable=False),
    )

    # ========================
    # 2) جدول واسط Product <-> SubscriptionType
    # ========================
    op.create_table(
        "product_subscription_type",
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("subscription_type_id", sa.Integer(), sa.ForeignKey("subscription_types.id"), primary_key=True),
    )

    # ========================
    # 3) جدول واسط Product <-> DurationType
    # ========================
    op.create_table(
        "product_duration_type",
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("duration_type_id", sa.Integer(), sa.ForeignKey("duration_types.id"), primary_key=True),
    )


def downgrade():
    # ========================
    # حذف جدول‌های واسط
    # ========================
    op.drop_table("product_duration_type")
    op.drop_table("product_subscription_type")

    # ========================
    # حذف CartItem و Cart
    # ========================
    op.drop_table("cart_items")
    op.drop_table("carts")
