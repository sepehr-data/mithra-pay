from __future__ import annotations
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from app.domain.entities.cart import Cart
from app.domain.entities.cart_item import CartItem
from app.domain.repositories.cart_repository import ICartRepository


class SQLAlchemyCartRepository(ICartRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_active_cart(self, user_id: int) -> Optional[Cart]:
        return (
            self.db.query(Cart)
            .options(selectinload(Cart.items))
            .filter(Cart.user_id == user_id, Cart.status == "ACTIVE")
            .first()
        )

    def create(self, cart: Cart) -> Cart:
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def add_item(self, item: CartItem) -> CartItem:
        existing = (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == item.cart_id,
                CartItem.product_id == item.product_id,
                (CartItem.subscription_type_id == item.subscription_type_id)
                if item.subscription_type_id is not None
                else CartItem.subscription_type_id.is_(None),
                (CartItem.duration_type_id == item.duration_type_id)
                if item.duration_type_id is not None
                else CartItem.duration_type_id.is_(None),
                CartItem.personal_account == bool(item.personal_account),
            )
            .first()
        )

        if existing:
            existing.quantity = int(existing.quantity or 0) + int(item.quantity or 0)
            existing.unit_price = item.unit_price
            existing.line_total = Decimal(str(existing.unit_price)) * Decimal(existing.quantity)

            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_item_in_cart(self, cart_id: int, cart_item_id: int) -> Optional[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(CartItem.id == cart_item_id, CartItem.cart_id == cart_id)
            .first()
        )

    def remove_item(self, cart_item_id: int) -> None:
        item = self.db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()

    def clear_cart(self, cart_id: int) -> None:
        self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete(synchronize_session=False)
        self.db.commit()

    def list_items(self, cart_id: int) -> List[CartItem]:
        return self.db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

    def update_item(self, item: CartItem) -> CartItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
