# app/domain/repositories/ticket_repository.py
from typing import Optional, List
from abc import ABC, abstractmethod
from app.domain.entities.ticket import Ticket


class ITicketRepository(ABC):
    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        pass

    @abstractmethod
    def list(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        pass

    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket:
        pass

