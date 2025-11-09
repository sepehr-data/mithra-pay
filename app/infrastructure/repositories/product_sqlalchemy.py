# app/infrastructure/repositories/product_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import IProductRepository


class SQLAlchemyProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.slug == slug).first()

    def list_products(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Product]:
        q = self.db.query(Product)

        if is_active is not None:
            q = q.filter(Product.is_active == is_active)

        if category_id is not None:
            q = q.filter(Product.category_id == category_id)

        if search:
            like = f"%{search}%"
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
