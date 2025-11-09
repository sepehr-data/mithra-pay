from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.infrastructure.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
