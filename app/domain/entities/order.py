from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from app.infrastructure.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(String(50), default="PENDING")          # PENDING, PAID, CANCELLED, FULFILLED
    payment_status = Column(String(50), default="UNPAID")   # UNPAID, PAID, FAILED
    total_amount = Column(DECIMAL(10, 2), default=0)
    currency = Column(String(10), default="IRR")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
