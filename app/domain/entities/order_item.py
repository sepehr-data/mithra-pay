from sqlalchemy import Column, Integer, ForeignKey, String, DECIMAL
from app.infrastructure.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    title_snapshot = Column(String(255))
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, default=1)
    line_total = Column(DECIMAL(10, 2), nullable=False)
