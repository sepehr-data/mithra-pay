from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    excerpt = Column(String(500))
    content = Column(Text)
    cover_image = Column(String(500))
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    author_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category_id = Column(Integer, ForeignKey("blog_category.id", ondelete="SET NULL"), nullable=True)
    category = relationship("BlogCategory", back_populates="posts")

