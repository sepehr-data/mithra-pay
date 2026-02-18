from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from app.domain.entities.product_relations import product_duration_types


class DurationType(Base):
    __tablename__ = "duration_types"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    products_legacy = relationship("Product", back_populates="duration_type_legacy")

    products_m2m = relationship(
        "Product",
        secondary=product_duration_types,
        back_populates="duration_types",
        lazy="selectin",
    )
