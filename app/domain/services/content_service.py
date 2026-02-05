# app/domain/services/content_service.py
from typing import List
from app.domain.repositories.blog_repository import IBlogRepository
from app.domain.entities.blog_post import BlogPost
from app.core import exceptions


class ContentService:
    def __init__(self, blog_repo: IBlogRepository | None = None):
        self.blog_repo = blog_repo

    def set_blog_repo(self, blog_repo: IBlogRepository):
        self.blog_repo = blog_repo

    def list_posts(self, limit: int = 50, offset: int = 0) -> List[BlogPost]:
        if not self.blog_repo:
            raise RuntimeError("BlogRepository not set")
        return self.blog_repo.list_posts(is_published=True, limit=limit, offset=offset)

    def get_post(self, slug: str) -> BlogPost:
        if not self.blog_repo:
            raise RuntimeError("BlogRepository not set")
        post = self.blog_repo.get_by_slug(slug)
        if not post or not post.is_published:
            raise exceptions.NotFoundError("post not found")
        return post

    def to_dict(self, p: BlogPost) -> dict:

        return {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "excerpt": getattr(p, "excerpt", None),
            "content": getattr(p, "content", None),
            "cover_image": getattr(p, "cover_image", None),

            "is_published": getattr(p, "is_published", False),
            "author_name": getattr(p, "author_name", None),
            "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
            "updated_at": p.updated_at.isoformat() if getattr(p, "updated_at", None) else None,

            "category_id": getattr(p, "category_id", None),

            # published_at
            "published_at": p.published_at.isoformat() if getattr(p, "published_at", None) else None,
        }
