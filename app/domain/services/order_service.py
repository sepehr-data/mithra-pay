# app/domain/services/order_service.py
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime
import random
import string

from app.domain.repositories.order_repository import IOrderRepository
from app.domain.repositories.product_repository import IProductRepository
from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.core import exceptions


def _generate_order_number() -> str:
    # simple human-readable order number
    return datetime.utcnow().strftime("%Y%m%d") + "-" + "".join(
        random.choices(string.digits, k=6)
    )


class OrderService:
    def __init__(
        self,
        order_repo: IOrderRepository | None = None,
        product_repo: IProductRepository | None = None,
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def set_repos(self, order_repo: IOrderRepository, product_repo: IProductRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def create_order(self, user_id: int, items: List[Dict[str, Any]]) -> Order:
        """
        items = [
            {"product_id": 1, "quantity": 2},
            ...
        ]
        """
        if not self.order_repo or not self.product_repo:
            raise RuntimeError("OrderService repositories not set")

        if not items:
            raise exceptions.ValidationError("order must contain at least one item")

        order_items: List[OrderItem] = []
        total = Decimal("0.00")

        for it in items:
            product_id = it.get("product_id")
            qty = int(it.get("quantity", 1))

            product = self.product_repo.get_by_id(product_id)
            if not product or not product.is_active:
                raise exceptions.NotFoundError(f"product {product_id} not available")

            unit_price = Decimal(str(product.price))
            line_total = unit_price * qty
            total += line_total

            order_item = OrderItem(
                product_id=product.id,
                title_snapshot=product.title,
                unit_price=unit_price,
                quantity=qty,
                line_total=line_total,
            )
            order_items.append(order_item)

        order = Order(
            order_number=_generate_order_number(),
            user_id=user_id,
            status="PENDING",
            payment_status="UNPAID",
            total_amount=total,
            currency="IRR",
        )

        created_order = self.order_repo.create_order(order, order_items)
        return created_order

    def get_order(self, order_id: int) -> Order:
        if not self.order_repo:
            raise RuntimeError("OrderService repositories not set")

        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise exceptions.NotFoundError("order not found")
        return order

    # helper for controllers
    def to_dict(self, order: Order) -> dict:
        return {
            "id": order.id,
            "order_number": order.order_number,
            "user_id": order.user_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_amount": float(order.total_amount) if order.total_amount is not None else 0,
            "currency": order.currency,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }
