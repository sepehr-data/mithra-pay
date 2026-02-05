# app/domain/repositories/ticket_repository.py
from typing import Optional, List
from abc import ABC, abstractmethod
from app.domain.entities.ticket import Ticket


class ITicketRepository(ABC):
    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """گرفتن یک تیکت بر اساس id"""
        pass

    @abstractmethod
    def list(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        """گرفتن لیستی از تیکت‌ها با امکان فیلتر بر اساس وضعیت"""
        pass

    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket:
        """ایجاد یک تیکت جدید"""
        pass

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket:
        """آپدیت یک تیکت موجود"""
        pass

