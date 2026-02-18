from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from app.domain.entities.product_relations import product_subscription_types, product_duration_types


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)

    price = Column(DECIMAL(10, 2), nullable=False)
    compare_at_price = Column(DECIMAL(10, 2))

    delivery_type = Column(String(50))
    platform = Column(String(100))

    duration_type_id = Column(Integer, ForeignKey("duration_types.id"), nullable=True, index=True)
    subscription_type_id = Column(Integer, ForeignKey("subscription_types.id"), nullable=True, index=True)

    duration_type_legacy = relationship("DurationType", back_populates="products_legacy")
    subscription_type_legacy = relationship("SubscriptionType", back_populates="products_legacy")

    subscription_types = relationship(
        "SubscriptionType",
        secondary=product_subscription_types,
        back_populates="products_m2m",
        lazy="selectin",
    )

    duration_types = relationship(
        "DurationType",
        secondary=product_duration_types,
        back_populates="products_m2m",
        lazy="selectin",
    )

    plan_prices = relationship(
        "ProductPlanPrice",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    personal_account = Column(Boolean, default=False, nullable=False)

    duration = Column(String(100))
    subscription_type = Column(String(50))

    region = Column(String(50))
    stock = Column(Integer)
    is_active = Column(Boolean, default=True)

    image_url = Column(String(500))
    short_description = Column(String(500))
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
