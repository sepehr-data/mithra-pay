from __future__ import annotations
from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped
from app.infrastructure.db.base import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        backref="cart",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
