"""create blog_category, link to blog_posts, seed initial categories

Revision ID: 1c2f3a4b5d6e
Revises: aaa7efbc5050
Create Date: 2026-02-02 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1c2f3a4b5d6e"
down_revision: str = "aaa7efbc5050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) create blog_category table
    op.create_table(
        "blog_category",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("slug", name="uq_blog_category_slug"),
    )
    op.create_index("ix_blog_category_name", "blog_category", ["name"])
    op.create_index("ix_blog_category_is_active", "blog_category", ["is_active"])

    # 2) add category_id to blog_posts (nullable for existing rows)
    op.add_column("blog_posts", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_index("ix_blog_posts_category_id", "blog_posts", ["category_id"])

    # 3) add FK (ON DELETE SET NULL)
    op.create_foreign_key(
        "fk_blog_posts_category_id",
        source_table="blog_posts",
        referent_table="blog_category",
        local_cols=["category_id"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )

    # 4) seed initial categories (idempotent)
    conn = op.get_bind()

    categories = [
        {"name": "موسیقی و استریم", "slug": "music-streaming"},
        {"name": "فیلم و سریال", "slug": "movies-series"},
        {"name": "اپل و آیکلود", "slug": "apple-icloud"},
        {"name": "یوتیوب و شبکه‌های اجتماعی", "slug": "youtube-social"},
        {"name": "گیمینگ و گیفت‌کارت", "slug": "gaming-giftcard"},
        {"name": "آموزش و راهنما", "slug": "tutorials-guides"},
        {"name": "اخبار و بروزرسانی‌ها", "slug": "news-updates"},
        {"name": "نکته‌ها و ترفندها", "slug": "tips-tricks"},
    ]

    stmt = sa.text(
        """
        INSERT INTO blog_category (name, slug, is_active, created_at, updated_at)
        VALUES (:name, :slug, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE
          name = VALUES(name),
          is_active = 1,
          updated_at = CURRENT_TIMESTAMP
        """
    )

    for c in categories:
        conn.execute(stmt, c)


def downgrade() -> None:
    op.drop_constraint("fk_blog_posts_category_id", "blog_posts", type_="foreignkey")
    op.drop_index("ix_blog_posts_category_id", table_name="blog_posts")
    op.drop_column("blog_posts", "category_id")

    op.drop_index("ix_blog_category_is_active", table_name="blog_category")
    op.drop_index("ix_blog_category_name", table_name="blog_category")
    op.drop_table("blog_category")
