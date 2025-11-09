# app/domain/services/product_service.py
from typing import Optional, List
from app.domain.repositories.product_repository import IProductRepository
from app.domain.entities.product import Product
from app.core import exceptions


class ProductService:
    def __init__(self, product_repo: IProductRepository | None = None):
        self.product_repo = product_repo

    def set_product_repo(self, product_repo: IProductRepository):
        self.product_repo = product_repo

    def list_products(
        self,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Product]:
        if not self.product_repo:
            raise RuntimeError("ProductRepository not set")

        # Note: if repo expects category_id, you can map slug -> id in repo impl
        products = self.product_repo.list_products(
            category_id=None,  # leave None here; map in infra if needed
            search=search,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        return products

    def get_product(self, product_id: int) -> Product:
        if not self.product_repo:
            raise RuntimeError("ProductRepository not set")

        prod = self.product_repo.get_by_id(product_id)
        if not prod:
            raise exceptions.NotFoundError("product not found")
        return prod

    # helper for controllers
    def to_dict(self, p: Product) -> dict:
        return {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "category_id": p.category_id,
            "price": float(p.price) if p.price is not None else None,
            "compare_at_price": float(p.compare_at_price) if p.compare_at_price else None,
            "delivery_type": p.delivery_type,
            "platform": p.platform,
            "duration": p.duration,
            "region": p.region,
            "stock": p.stock,
            "is_active": p.is_active,
            "image_url": p.image_url,
            "short_description": p.short_description,
            "description": p.description,
        }
