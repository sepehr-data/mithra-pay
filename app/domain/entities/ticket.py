from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.infrastructure.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    subject = Column(String(50), nullable=False)
    order_number = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)

    # وضعیت تیکت: OPEN, IN_PROGRESS, CLOSED
    status = Column(String(50), default="open")
    accepted_policy = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # در صورت نیاز به ربط با کاربر ثبت‌نام شده
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
