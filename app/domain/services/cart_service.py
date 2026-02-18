# app/domain/services/cart_service.py
from __future__ import annotations

from decimal import Decimal

from app.domain.entities.cart import Cart
from app.domain.entities.cart_item import CartItem
from app.domain.repositories.cart_repository import ICartRepository
from app.domain.repositories.product_repository import IProductRepository
from app.core import exceptions


class CartService:
    def __init__(self, cart_repo: ICartRepository, product_repo: IProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def get_or_create_cart(self, user_id: int) -> Cart:
        cart = self.cart_repo.get_active_cart(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            self.cart_repo.create(cart)
        return cart

    @staticmethod
    def _decimal(v) -> Decimal:
        if v is None:
            return Decimal("0")
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))

    def _resolve_unit_price(
        self,
        product,
        subscription_type_id: int | None,
        duration_type_id: int | None
    ) -> Decimal:

        base = self._decimal(getattr(product, "price", None))

        if subscription_type_id and duration_type_id:
            for row in (getattr(product, "plan_prices", []) or []):
                if (
                    getattr(row, "subscription_type_id", None) == subscription_type_id
                    and getattr(row, "duration_type_id", None) == duration_type_id
                ):
                    return self._decimal(getattr(row, "price", None))

        return base

    def add_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int = 1,
        duration_type_id: int | None = None,
        subscription_type_id: int | None = None,
        personal_account: bool = False,
    ) -> CartItem:
        if quantity <= 0:
            quantity = 1

        cart = self.get_or_create_cart(user_id)

        product = self.product_repo.get_by_id(product_id)
        if not product or not getattr(product, "is_active", False):
            raise exceptions.NotFoundError("product not found or inactive")

        unit_price = self._resolve_unit_price(product, subscription_type_id, duration_type_id)
        line_total = unit_price * Decimal(quantity)

        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            title_snapshot=getattr(product, "title", ""),
            unit_price=unit_price,
            quantity=quantity,
            line_total=line_total,
            duration_type_id=duration_type_id,
            subscription_type_id=subscription_type_id,
            personal_account=personal_account,
        )
        return self.cart_repo.add_item(item)

    def remove_item(self, user_id: int, cart_item_id: int) -> None:
        cart = self.cart_repo.get_active_cart(user_id)
        if not cart:
            return

        if hasattr(self.cart_repo, "get_item_in_cart"):
            item = self.cart_repo.get_item_in_cart(cart.id, cart_item_id)
            if not item:
                return
            self.cart_repo.remove_item(cart_item_id)
            return

        self.cart_repo.remove_item(cart_item_id)

    def get_cart(self, user_id: int) -> Cart:
        return self.get_or_create_cart(user_id)

    def clear_cart(self, user_id: int) -> None:
        cart = self.get_or_create_cart(user_id)
        self.cart_repo.clear_cart(cart.id)

    def update_item_quantity(self, user_id: int, cart_item_id: int, quantity: int) -> CartItem:
        if quantity <= 0:
            quantity = 1

        cart = self.cart_repo.get_active_cart(user_id)
        if not cart:
            raise exceptions.NotFoundError("cart not found")

        if hasattr(self.cart_repo, "get_item_in_cart"):
            item = self.cart_repo.get_item_in_cart(cart.id, cart_item_id)
        else:
            item = None

        if not item:
            raise exceptions.NotFoundError("cart item not found")

        item.quantity = int(quantity)
        item.line_total = self._decimal(item.unit_price) * Decimal(item.quantity)

        if hasattr(self.cart_repo, "update_item"):
            return self.cart_repo.update_item(item)

        return self.cart_repo.add_item(item)
