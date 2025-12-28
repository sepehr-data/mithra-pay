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

    def get_top_selling_products_this_week(self, limit: int = 8) -> List[Product]:
        if not self.product_repo:
            raise RuntimeError("ProductRepository not set")

        return self.product_repo.get_top_selling_products_for_last_days(
            days=7, limit=limit
        )

    def create_product(
        self,
        title: str,
        slug: str,
        category_id: int,
        price: float,
        compare_at_price: float | None = None,
        delivery_type: str | None = None,
        platform: str | None = None,
        duration: str | None = None,
        region: str | None = None,
        stock: int | None = None,
        is_active: bool = True,
        image_url: str | None = None,
        short_description: str | None = None,
        description: str | None = None,
    ) -> Product:
        if not self.product_repo:
            raise RuntimeError("ProductRepository not set")

        if not title:
            raise exceptions.ValidationError("title is required")
        if not slug:
            raise exceptions.ValidationError("slug is required")
        if category_id is None:
            raise exceptions.ValidationError("category_id is required")
        if price is None:
            raise exceptions.ValidationError("price is required")

        product = Product(
            title=title,
            slug=slug,
            category_id=category_id,
            price=price,
            compare_at_price=compare_at_price,
            delivery_type=delivery_type,
            platform=platform,
            duration=duration,
            region=region,
            stock=stock,
            is_active=is_active,
            image_url=image_url,
            short_description=short_description,
            description=description,
        )

        return self.product_repo.create(product)

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
