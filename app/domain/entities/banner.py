from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.infrastructure.db.base import Base

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    link = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=False)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

