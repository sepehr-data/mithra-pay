# app/infrastructure/repositories/cart_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities.cart import Cart
from app.domain.entities.cart_item import CartItem
from app.domain.repositories.cart_repository import ICartRepository


class SQLAlchemyCartRepository(ICartRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> Optional[Cart]:
        return self.db.query(Cart).filter(Cart.user_id == user_id).first()

    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        return self.db.query(Cart).filter(Cart.id == cart_id).first()

    def create(self, cart: Cart) -> Cart:
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def get_items(self, cart_id: int) -> List[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id)
            .order_by(CartItem.id.asc())
            .all()
        )

    def get_item_by_id(self, item_id: int) -> Optional[CartItem]:
        return self.db.query(CartItem).filter(CartItem.id == item_id).first()

    def get_item_by_cart_and_product(
        self, cart_id: int, product_id: int
    ) -> Optional[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .first()
        )

    def add_item(self, item: CartItem) -> CartItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item: CartItem) -> CartItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: CartItem) -> None:
        self.db.delete(item)
        self.db.commit()

    def clear_items(self, cart_id: int) -> None:
        self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        self.db.commit()
