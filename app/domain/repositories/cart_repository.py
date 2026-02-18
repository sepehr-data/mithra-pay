# app/domain/repositories/cart_repository.py
from abc import ABC, abstractmethod
from app.domain.entities.cart import Cart
from app.domain.entities.cart_item import CartItem
from typing import List, Optional


class ICartRepository(ABC):

    @abstractmethod
    def get_active_cart(self, user_id: int) -> Optional[Cart]:
        """برگرداندن کارت فعال کاربر"""
        pass

    @abstractmethod
    def create(self, cart: Cart) -> Cart:
        """ایجاد کارت جدید"""
        pass

    @abstractmethod
    def add_item(self, item: CartItem) -> CartItem:
        """افزودن آیتم به کارت"""
        pass

    @abstractmethod
    def remove_item(self, cart_item_id: int) -> None:
        """حذف آیتم از کارت"""
        pass

    @abstractmethod
    def clear_cart(self, cart_id: int) -> None:
        """خالی کردن کارت"""
        pass

    @abstractmethod
    def list_items(self, cart_id: int) -> List[CartItem]:
        """لیست آیتم‌های کارت"""
        pass
