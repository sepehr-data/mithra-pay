from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from app.domain.entities.product_relations import product_subscription_types


class SubscriptionType(Base):
    __tablename__ = "subscription_types"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    products_legacy = relationship("Product", back_populates="subscription_type_legacy")

    products_m2m = relationship(
        "Product",
        secondary=product_subscription_types,
        back_populates="subscription_types",
        lazy="selectin",
    )
