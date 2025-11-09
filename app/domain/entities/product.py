from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL
from app.infrastructure.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    compare_at_price = Column(DECIMAL(10, 2))
    delivery_type = Column(String(50))  # INSTANT_CODE, MANUAL_ACTIVATION, SHARED_ACCOUNT
    platform = Column(String(100))      # apple, netflix, youtube, ...
    duration = Column(String(100))      # e.g. "1 month", "3 months"
    region = Column(String(50))         # e.g. "TR", "US"
    stock = Column(Integer)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(500))
    short_description = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
