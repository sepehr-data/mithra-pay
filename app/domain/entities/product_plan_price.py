from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, DECIMAL
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class ProductPlanPrice(Base):
    __tablename__ = "product_plan_prices"
    __table_args__ = (
        UniqueConstraint("product_id", "subscription_type_id", "duration_type_id", name="uq_product_plan_price"),
    )

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_type_id = Column(Integer, ForeignKey("subscription_types.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_type_id = Column(Integer, ForeignKey("duration_types.id", ondelete="CASCADE"), nullable=False, index=True)

    price = Column(DECIMAL(10, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="plan_prices")
    subscription_type = relationship("SubscriptionType")
    duration_type = relationship("DurationType")
