# app/domain/repositories/cart_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.entities.cart import Cart
from app.domain.entities.cart_item import CartItem


class ICartRepository(ABC):
    @abstractmethod
    def get_by_user(self, user_id: int) -> Optional[Cart]:
        ...

    @abstractmethod
    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        ...

    @abstractmethod
    def create(self, cart: Cart) -> Cart:
        ...

    @abstractmethod
    def get_items(self, cart_id: int) -> List[CartItem]:
        ...

    @abstractmethod
    def get_item_by_id(self, item_id: int) -> Optional[CartItem]:
        ...

    @abstractmethod
    def get_item_by_cart_and_product(
        self, cart_id: int, product_id: int
    ) -> Optional[CartItem]:
        ...

    @abstractmethod
    def add_item(self, item: CartItem) -> CartItem:
        ...

    @abstractmethod
    def update_item(self, item: CartItem) -> CartItem:
        ...

    @abstractmethod
    def delete_item(self, item: CartItem) -> None:
        ...

    @abstractmethod
    def clear_items(self, cart_id: int) -> None:
        ...
