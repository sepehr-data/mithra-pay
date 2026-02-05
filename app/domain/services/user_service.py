# app/domain/services/user_service.py
from typing import Optional, Dict, Any
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.core.security import hash_password
from app.core import exceptions


class UserService:
    def __init__(self, user_repo: IUserRepository | None = None):
        self.user_repo = user_repo

    def set_repo(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def get_user(self, user_id: int) -> User:
        if not self.user_repo:
            raise RuntimeError("UserService repository not set")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise exceptions.NotFoundError("user not found")
        return user

    def update_user(self, user_id: int, data: Dict[str, Any]) -> User:
        if not self.user_repo:
            raise RuntimeError("UserService repository not set")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise exceptions.NotFoundError("user not found")

        if "name" in data:
            user.first_name = data["name"] or None
        if "last_name" in data:
            user.last_name = data["last_name"] or None
        if "national_id" in data:
            user.national_id = data["national_id"] or None
        if "email" in data:
            user.email = data["email"] or None
        if "sheba" in data:
            user.sheba = data["sheba"] or None
        if "bank_number" in data:
            user.bank_number = data["bank_number"] or None
        if "phone" in data:
            user.phone = data["phone"] or None
        if "birthday" in data:
            user.birthday = data["birthday"] or None

        if data.get("password"):
            user.password_hash = hash_password(data["password"])

        self.user_repo.update(user)
        return user

    def to_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "phone": getattr(user, "phone", None),
            "name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "national_id": getattr(user, "national_id", None),
            "email": getattr(user, "email", None),
            "birthday": getattr(user, "birthday", None),
            "sheba": getattr(user, "sheba", None),
            "bank_number": getattr(user, "bank_number", None),
        }
