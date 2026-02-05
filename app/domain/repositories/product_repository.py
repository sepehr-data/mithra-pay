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
        duration_type_id: Optional[int] = None,
        subscription_type_id: Optional[int] = None,
        personal_account: Optional[bool] = None,
    ) -> List[Product]:
        ...

    @abstractmethod
    def count_products(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        duration_type_id: Optional[int] = None,
        subscription_type_id: Optional[int] = None,
        personal_account: Optional[bool] = None,
    ) -> int:
        ...

    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def update(self, product: Product) -> Product:
        ...
