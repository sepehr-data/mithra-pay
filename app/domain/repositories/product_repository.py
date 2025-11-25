# app/domain/repositories/product_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.product import Product


class IProductRepository(ABC):
    """
    Product repository interface for MithraPay products
    (digital, gift card, physical).
    """

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Product]:
        ...

    @abstractmethod
    def list_products(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Product]:
        ...

    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def update(self, product: Product) -> Product:
        ...

    @abstractmethod
    def get_top_selling_products_for_last_days(
        self, days: int, limit: int = 8
    ) -> List[Product]:
        ...
