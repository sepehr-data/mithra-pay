# app/infrastructure/repositories/order_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.repositories.order_repository import IOrderRepository


class SQLAlchemyOrderRepository(IOrderRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.order_number == order_number).first()

    def list_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Order]:
        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create_order(self, order: Order, items: List[OrderItem]) -> Order:
        """
        Persist order and its items in one transaction.
        """
        self.db.add(order)
        self.db.flush()  # so order.id is available

        for it in items:
            it.order_id = order.id
            self.db.add(it)

        self.db.commit()
        self.db.refresh(order)
        return order

    def add_item(self, order_item: OrderItem) -> OrderItem:
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        return order_item

    def update(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
