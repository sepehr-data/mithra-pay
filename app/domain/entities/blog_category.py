from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class BlogCategory(Base):
    __tablename__ = "blog_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(160), nullable=False, index=True, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = relationship("BlogPost", back_populates="category")

