from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, DECIMAL, Text
from app.infrastructure.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default="INIT")   # INIT, SUCCESS, FAILED
    gateway = Column(String(50))
    gateway_ref = Column(String(255))
    tracking_code = Column(String(255))
    raw_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
