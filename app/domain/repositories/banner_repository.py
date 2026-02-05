# app/domain/repositories/banner_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.banner import Banner


class IBannerRepository(ABC):
    """
    Banner repository interface.
    """

    @abstractmethod
    def get_by_id(self, banner_id: int) -> Optional[Banner]:
        ...

    @abstractmethod
    def list(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Banner]:
        ...

    @abstractmethod
    def create(self, banner: Banner) -> Banner:
        ...

    @abstractmethod
    def update(self, banner: Banner) -> Banner:
        ...

    @abstractmethod
    def delete(self, banner_id: int) -> None:
        ...

