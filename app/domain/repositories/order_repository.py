# app/domain/repositories/order_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem


class IOrderRepository(ABC):
    """
    Order repository interface.
    Handles both orders and their items.
    """

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Order]:
        ...

    @abstractmethod
    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        ...

    @abstractmethod
    def list_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Order]:
        ...

    @abstractmethod
    def create_order(self, order: Order, items: List[OrderItem]) -> Order:
        """
        Persist order + its items in one transaction.
        """
        ...

    @abstractmethod
    def add_item(self, order_item: OrderItem) -> OrderItem:
        ...

    @abstractmethod
    def update(self, order: Order) -> Order:
        ...
