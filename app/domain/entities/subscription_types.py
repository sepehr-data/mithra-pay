from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class SubscriptionType(Base):
    __tablename__ = "subscription_types"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    products = relationship("Product", back_populates="subscription_type_rel")
