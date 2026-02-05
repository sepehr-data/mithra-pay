from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload

from app.domain.entities.product import Product
from app.domain.entities.order_item import OrderItem
from app.domain.entities.order import Order
from app.domain.repositories.product_repository import IProductRepository


class SQLAlchemyProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        q = self.db.query(Product)
        if hasattr(Product, "duration_type"):
            q = q.options(joinedload(Product.duration_type))
        if hasattr(Product, "subscription_type_rel"):
            q = q.options(joinedload(Product.subscription_type_rel))
        return q.filter(Product.id == product_id).first()

    def get_by_slug(self, slug: str) -> Optional[Product]:
        q = self.db.query(Product)
        if hasattr(Product, "duration_type"):
            q = q.options(joinedload(Product.duration_type))
        if hasattr(Product, "subscription_type_rel"):
            q = q.options(joinedload(Product.subscription_type_rel))
        return q.filter(Product.slug == slug).first()

    def list_products(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
        duration_type_id: Optional[int] = None,
        subscription_type_id: Optional[int] = None,
        personal_account: Optional[bool] = None,
    ) -> List[Product]:
        q = self.db.query(Product)

        # eager load relationships if exist
        if hasattr(Product, "duration_type"):
            q = q.options(joinedload(Product.duration_type))
        if hasattr(Product, "subscription_type_rel"):
            q = q.options(joinedload(Product.subscription_type_rel))

        if is_active is not None:
            q = q.filter(Product.is_active == is_active)

        if category_id is not None:
            q = q.filter(Product.category_id == category_id)

        if duration_type_id is not None and hasattr(Product, "duration_type_id"):
            q = q.filter(Product.duration_type_id == duration_type_id)

        if subscription_type_id is not None and hasattr(Product, "subscription_type_id"):
            q = q.filter(Product.subscription_type_id == subscription_type_id)

        if personal_account is not None and hasattr(Product, "personal_account"):
            q = q.filter(Product.personal_account == personal_account)

        if search:
            like = f"%{search}%"
            # نکته: ممکنه platform بعضی رکوردها NULL باشه
            q = q.filter(
                or_(
                    Product.title.ilike(like),
                    Product.slug.ilike(like),
                    Product.platform.ilike(like),
                )
            )

        return (
            q.order_by(Product.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_products(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        duration_type_id: Optional[int] = None,
        subscription_type_id: Optional[int] = None,
        personal_account: Optional[bool] = None,
    ) -> int:
        q = self.db.query(func.count(Product.id))

        if is_active is not None:
            q = q.filter(Product.is_active == is_active)

        if category_id is not None:
            q = q.filter(Product.category_id == category_id)

        if duration_type_id is not None and hasattr(Product, "duration_type_id"):
            q = q.filter(Product.duration_type_id == duration_type_id)

        if subscription_type_id is not None and hasattr(Product, "subscription_type_id"):
            q = q.filter(Product.subscription_type_id == subscription_type_id)

        if personal_account is not None and hasattr(Product, "personal_account"):
            q = q.filter(Product.personal_account == personal_account)

        if search:
            like = f"%{search}%"
            q = q.filter(
                or_(
                    Product.title.ilike(like),
                    Product.slug.ilike(like),
                    Product.platform.ilike(like),
                )
            )

        return int(q.scalar() or 0)

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int):
        self.db.query(Product).filter(Product.id == product_id).delete()
        self.db.commit()

    def get_top_selling_products_for_last_days(
        self, days: int, limit: int = 8
    ) -> List[Product]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_sold = func.sum(OrderItem.quantity).label("total_sold")

        q = (
            self.db.query(Product)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.created_at >= cutoff_date)
            .group_by(Product.id)
            .order_by(total_sold.desc())
            .limit(limit)
        )

        # eager load if relationships exist
        if hasattr(Product, "duration_type"):
            q = q.options(joinedload(Product.duration_type))
        if hasattr(Product, "subscription_type_rel"):
            q = q.options(joinedload(Product.subscription_type_rel))

        return q.all()
