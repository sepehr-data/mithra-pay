# app/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User
from app.domain.entities.role import Role

class IUserRepository(ABC):
    """
    User repository interface.
    Domain services depend on this, not on SQLAlchemy directly.
    """

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[User]:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        ...

    @abstractmethod
    def create(self, user: User) -> User:
        ...

    @abstractmethod
    def update(self, user: User) -> User:
        ...

    @abstractmethod
    def get_roles(self, user_id: int) -> List[Role]:
        """
        Return all roles for a user.
        Needed to embed roles into JWT.
        """
        ...