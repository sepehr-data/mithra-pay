# app/domain/repositories/payment_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.payment import Payment


class IPaymentRepository(ABC):
    """
    Payment repository interface.
    Used for saving gateway init/callback data.
    """

    @abstractmethod
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        ...

    @abstractmethod
    def list_by_order(self, order_id: int) -> List[Payment]:
        ...

    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        ...

    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        ...
