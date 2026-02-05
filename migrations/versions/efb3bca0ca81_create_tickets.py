"""create_tickets

Revision ID: efb3bca0ca81
Revises: d2a30329bf87
Create Date: 2026-01-24 13:50:40.353817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = 'efb3bca0ca81'
down_revision: Union[str, Sequence[str], None] = 'd2a30329bf87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.drop_table('banners')
    op.drop_index(op.f('name'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_cart_items_cart_id'), table_name='cart_items')
    op.drop_index(op.f('ix_cart_items_product_id'), table_name='cart_items')
    op.drop_table('cart_items')
    op.drop_index(op.f('ix_carts_user_id'), table_name='carts')
    op.drop_table('carts')
    op.drop_index(op.f('ix_products_category_id'), table_name='products')
    op.drop_index(op.f('ix_products_slug'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_blog_posts_slug'), table_name='blog_posts')
    op.drop_table('blog_posts')
    op.drop_index(op.f('uq_user_role'), table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_table('tickets')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_table('categories')
    op.drop_index(op.f('key'), table_name='settings')
    op.drop_table('settings')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_orders_order_number'), table_name='orders')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_table('orders')


def downgrade() -> None:

    op.create_table('orders',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('order_number', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('status', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('payment_status', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('total_amount', mysql.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('currency', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='orders_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    op.create_index(op.f('ix_orders_order_number'), 'orders', ['order_number'], unique=True)
    op.create_table('users',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('first_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('last_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('phone', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('password_hash', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('is_phone_verified', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('national_id', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('bank_number', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('sheba', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('birthday', sa.DATE(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('settings',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('key', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('value', mysql.TEXT(), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('key'), 'settings', ['key'], unique=True)
    op.create_table('categories',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('slug', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('description', mysql.TEXT(), nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=False)
    op.create_table('tickets',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('subject', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('order_number', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('message', mysql.TEXT(), nullable=False),
    sa.Column('status', mysql.VARCHAR(length=50), server_default=sa.text("'OPEN'"), nullable=False),
    sa.Column('accepted_policy', mysql.TINYINT(display_width=1), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('current_timestamp()'), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), server_default=sa.text('current_timestamp()'), nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('tickets_ibfk_1')),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user_roles',
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('role_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('user_roles_ibfk_2')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('user_roles_ibfk_1')),
    sa.PrimaryKeyConstraint('user_id', 'role_id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('uq_user_role'), 'user_roles', ['user_id', 'role_id'], unique=True)
    op.create_table('blog_posts',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('slug', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('excerpt', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('content', mysql.TEXT(), nullable=True),
    sa.Column('cover_image', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('is_published', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('published_at', mysql.DATETIME(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('author_name', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_blog_posts_slug'), 'blog_posts', ['slug'], unique=False)
    op.create_table('order_items',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('order_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('product_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('title_snapshot', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('unit_price', mysql.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('quantity', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('line_total', mysql.DECIMAL(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name=op.f('order_items_ibfk_1')),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('order_items_ibfk_2')),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_table('payments',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('order_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('amount', mysql.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('status', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('gateway', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('gateway_ref', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('tracking_code', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('raw_response', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name=op.f('payments_ibfk_1')),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)
    op.create_table('products',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('slug', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('category_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('price', mysql.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('compare_at_price', mysql.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('delivery_type', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('platform', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('duration', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('region', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('stock', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('image_url', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('short_description', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('description', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='products_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_products_slug'), 'products', ['slug'], unique=False)
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)
    op.create_table('carts',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('status', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='carts_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_carts_user_id'), 'carts', ['user_id'], unique=False)
    op.create_table('cart_items',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('cart_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('product_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('title_snapshot', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('unit_price', mysql.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('quantity', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('line_total', mysql.DECIMAL(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], name=op.f('cart_items_ibfk_1')),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('cart_items_ibfk_2')),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_cart_items_product_id'), 'cart_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_cart_items_cart_id'), 'cart_items', ['cart_id'], unique=False)
    op.create_table('roles',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('name'), 'roles', ['name'], unique=True)
    op.create_table('banners',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('link', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('image_url', mysql.VARCHAR(length=500), nullable=False),
    sa.Column('status', mysql.VARCHAR(length=50), server_default=sa.text("'ACTIVE'"), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('current_timestamp()'), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), server_default=sa.text('current_timestamp()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
