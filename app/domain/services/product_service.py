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
        duration_type_id: Optional[int] = None,
        subscription_type_id: Optional[int] = None,
        personal_account: Optional[bool] = None,
    ) -> List[Product]:
        if not self.product_repo:
            raise RuntimeError("ProductRepository not set")

        try:
            return self.product_repo.list_products(
                category_id=None,
                search=search,
                is_active=is_active,
                limit=limit,
                offset=offset,
                duration_type_id=duration_type_id,
                subscription_type_id=subscription_type_id,
                personal_account=personal_account,
            )
        except TypeError:
            return self.product_repo.list_products(
                category_id=None,
                search=search,
                is_active=is_active,
                limit=limit,
                offset=offset,
            )

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
        return self.product_repo.get_top_selling_products_for_last_days(days=7, limit=limit)

    def create_product(
        self,
        title: str,
        slug: str,
        category_id: int,
        price: float,
        compare_at_price: float | None = None,
        delivery_type: str | None = None,
        platform: str | None = None,
        duration_type_id: int | None = None,
        subscription_type_id: int | None = None,
        personal_account: bool = False,
        duration: str | None = None,
        subscription_type: str | None = None,
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
            duration_type_id=duration_type_id,
            subscription_type_id=subscription_type_id,
            personal_account=personal_account,
            duration=duration,
            subscription_type=subscription_type,
            region=region,
            stock=stock,
            is_active=is_active,
            image_url=image_url,
            short_description=short_description,
            description=description,
        )

        return self.product_repo.create(product)

    def resolve_price_for(self, p: Product, subscription_type_id: int | None, duration_type_id: int | None):
        """
        If both ids provided and a matching row exists in plan_prices => return that
        else fallback to base product.price
        """
        if subscription_type_id and duration_type_id:
            for row in (getattr(p, "plan_prices", []) or []):
                if row.subscription_type_id == subscription_type_id and row.duration_type_id == duration_type_id:
                    try:
                        return float(row.price)
                    except Exception:
                        return p.price
        return float(p.price) if p.price is not None else None

    def to_dict(self, p: Product, *, subscription_type_id: int | None = None, duration_type_id: int | None = None) -> dict:
        dt = getattr(p, "duration_type", None)
        st = getattr(p, "subscription_type_rel", None)

        resolved_price = self.resolve_price_for(p, subscription_type_id, duration_type_id)

        return {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "category_id": p.category_id,

            # ✅ این price برای سایت، price درست ترکیب را برمی‌گرداند
            "price": resolved_price,
            "base_price": float(p.price) if p.price is not None else None,
            "compare_at_price": float(p.compare_at_price) if p.compare_at_price else None,

            "delivery_type": p.delivery_type,
            "platform": p.platform,

            "duration_type_id": getattr(p, "duration_type_id", None),
            "subscription_type_id": getattr(p, "subscription_type_id", None),
            "personal_account": getattr(p, "personal_account", False),

            "duration": getattr(p, "duration", None),
            "subscription_type": getattr(p, "subscription_type", None),

            "duration_type": (
                {"id": dt.id, "title": dt.title, "slug": dt.slug}
                if dt is not None else None
            ),
            "subscription_type_obj": (
                {"id": st.id, "title": st.title, "slug": st.slug}
                if st is not None else None
            ),

            "subscription_types": [
                {"id": s.id, "title": s.title, "slug": s.slug}
                for s in (getattr(p, "subscription_types", []) or [])
            ],

            "duration_types": [
                {"id": d.id, "title": d.title, "slug": d.slug}
                for d in (getattr(p, "duration_types", []) or [])
            ],

            # ✅ جدید: کل قیمت‌های ترکیبی (اگر خواستی روی سایت هم ماتریکس نشون بدی)
            "prices": [
                {
                    "subscription_type_id": row.subscription_type_id,
                    "duration_type_id": row.duration_type_id,
                    "price": float(row.price) if row.price is not None else None,
                }
                for row in (getattr(p, "plan_prices", []) or [])
            ],

            "region": p.region,
            "stock": p.stock,
            "is_active": p.is_active,
            "image_url": p.image_url,
            "short_description": p.short_description,
            "description": p.description,
        }
