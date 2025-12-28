from decimal import Decimal
from typing import List

from app.domain.entities.cart import Cart
from app.domain.entities.cart_item import CartItem
from app.domain.repositories.cart_repository import ICartRepository
from app.domain.repositories.product_repository import IProductRepository
from app.core import exceptions


class CartService:
    def __init__(
        self,
        cart_repo: ICartRepository | None = None,
        product_repo: IProductRepository | None = None,
    ):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def set_repos(
        self,
        cart_repo: ICartRepository,
        product_repo: IProductRepository,
    ):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def get_or_create_cart(self, user_id: int) -> Cart:
        if not self.cart_repo:
            raise RuntimeError("CartRepository not set")
        if not user_id:
            raise exceptions.ValidationError("user_id is required")

        cart = self.cart_repo.get_by_user(user_id)
        if cart:
            return cart

        return self.cart_repo.create(Cart(user_id=user_id, status="ACTIVE"))

    def get_cart(self, user_id: int) -> Cart | None:
        if not self.cart_repo:
            raise RuntimeError("CartRepository not set")
        if not user_id:
            raise exceptions.ValidationError("user_id is required")
        return self.cart_repo.get_by_user(user_id)

    def add_item(self, user_id: int, product_id: int, quantity: int = 1) -> Cart:
        if not self.cart_repo or not self.product_repo:
            raise RuntimeError("CartService repositories not set")
        if not user_id:
            raise exceptions.ValidationError("user_id is required")
        if not product_id:
            raise exceptions.ValidationError("product_id is required")
        if quantity <= 0:
            raise exceptions.ValidationError("quantity must be greater than zero")

        product = self.product_repo.get_by_id(product_id)
        if not product or not product.is_active:
            raise exceptions.NotFoundError("product not available")

        cart = self.get_or_create_cart(user_id)
        existing = self.cart_repo.get_item_by_cart_and_product(cart.id, product_id)
        if existing:
            existing.quantity = existing.quantity + quantity
            existing.line_total = Decimal(str(existing.unit_price)) * existing.quantity
            self.cart_repo.update_item(existing)
            return cart

        unit_price = Decimal(str(product.price))
        line_total = unit_price * quantity
        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            title_snapshot=product.title,
            unit_price=unit_price,
            quantity=quantity,
            line_total=line_total,
        )
        self.cart_repo.add_item(item)
        return cart

    def update_item(self, item_id: int, quantity: int) -> Cart:
        if not self.cart_repo:
            raise RuntimeError("CartRepository not set")
        if quantity <= 0:
            raise exceptions.ValidationError("quantity must be greater than zero")

        item = self.cart_repo.get_item_by_id(item_id)
        if not item:
            raise exceptions.NotFoundError("cart item not found")

        item.quantity = quantity
        item.line_total = Decimal(str(item.unit_price)) * quantity
        self.cart_repo.update_item(item)
        return self._get_cart_by_item(item)

    def remove_item(self, item_id: int) -> Cart:
        if not self.cart_repo:
            raise RuntimeError("CartRepository not set")
        item = self.cart_repo.get_item_by_id(item_id)
        if not item:
            raise exceptions.NotFoundError("cart item not found")
        self.cart_repo.delete_item(item)
        return self._get_cart_by_item(item)

    def clear_cart(self, user_id: int) -> None:
        if not self.cart_repo:
            raise RuntimeError("CartRepository not set")
        cart = self.cart_repo.get_by_user(user_id)
        if not cart:
            return
        self.cart_repo.clear_items(cart.id)

    def list_items(self, cart: Cart) -> List[CartItem]:
        if not self.cart_repo:
            raise RuntimeError("CartRepository not set")
        return self.cart_repo.get_items(cart.id)

    def to_dict(self, cart: Cart | None) -> dict:
        if not cart:
            return {"cart_id": None, "user_id": None, "items": [], "total_amount": 0}

        items = self.list_items(cart)
        total = sum((item.line_total for item in items), Decimal("0.00"))
        return {
            "cart_id": cart.id,
            "user_id": cart.user_id,
            "status": cart.status,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "title_snapshot": item.title_snapshot,
                    "unit_price": float(item.unit_price),
                    "quantity": item.quantity,
                    "line_total": float(item.line_total),
                }
                for item in items
            ],
            "total_amount": float(total),
        }

    def _get_cart_by_item(self, item: CartItem) -> Cart:
        cart = self.cart_repo.get_by_id(item.cart_id)
        if not cart:
            raise exceptions.NotFoundError("cart not found")
        return cart
