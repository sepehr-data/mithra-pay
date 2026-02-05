# app/infrastructure/repositories/blog_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import case

from app.domain.entities.blog_post import BlogPost
from app.domain.entities.blog_category import BlogCategory
from app.domain.entities.blog_post import BlogPost as BlogPostModel
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
            is_published: Optional[bool] = None,
            limit: int = 50,
            offset: int = 0,
    ) -> List["BlogPostModel"]:
        q = self.db.query(BlogPostModel)

        if is_published is not None:
            q = q.filter(BlogPostModel.is_published == is_published)

        return (
            q.order_by(
                case(
                    (BlogPostModel.published_at.is_(None), 1),
                    else_=0,
                ),
                BlogPostModel.published_at.desc(),
            )
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

    def delete(self, post_id: int) -> None:
        post = self.get_by_id(post_id)
        if not post:
            return

        self.db.delete(post)
        self.db.commit()

    def list_active(self):
        return (
            self.db.query(BlogCategory)
            .filter(BlogCategory.is_active == True)
            .order_by(BlogCategory.id.desc())
            .all()
        )

    def get_category_by_id(self, category_id: int) -> Optional[BlogCategory]:
        return self.db.query(BlogCategory).filter(BlogCategory.id == category_id).first()