from sqlalchemy import Column, Integer, String, Text
from app.infrastructure.db.base import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255))
