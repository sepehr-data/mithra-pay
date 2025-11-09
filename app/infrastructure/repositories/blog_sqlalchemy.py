# app/infrastructure/repositories/blog_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities.blog_post import BlogPost
from app.domain.repositories.blog_repository import IBlogRepository


class SQLAlchemyBlogRepository(IBlogRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, post_id: int) -> Optional[BlogPost]:
        return self.db.query(BlogPost).filter(BlogPost.id == post_id).first()

    def get_by_slug(self, slug: str) -> Optional[BlogPost]:
        return self.db.query(BlogPost).filter(BlogPost.slug == slug).first()

    def list_posts(
        self,
        is_published: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[BlogPost]:
        q = self.db.query(BlogPost)
        if is_published is not None:
            q = q.filter(BlogPost.is_published == is_published)
        return (
            q.order_by(BlogPost.published_at.desc().nullslast())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, post: BlogPost) -> BlogPost:
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post: BlogPost) -> BlogPost:
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
