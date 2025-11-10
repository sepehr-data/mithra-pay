# app/domain/services/auth_service.py
from typing import Optional, List

from app.core import exceptions
from app.core.security import hash_password, verify_password, create_access_token
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.domain.entities.role import Role


class AuthService:
    """
    Handles register/login and token issuing.
    This service needs a concrete IUserRepository injected.
    """

    def __init__(self, user_repo: IUserRepository | None = None):
        self.user_repo = user_repo

    def set_user_repo(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    # ---- internal helper ----------
    def _get_user_roles(self, user_id: int) -> List[str]:
        """
        Ask the repo for Role objects and return list of names.
        """
        if not self.user_repo:
            return []
        roles = self.user_repo.get_roles(user_id)
        return [r.name for r in roles]

    def _issue_token_with_roles(self, user: User) -> str:
        roles = self._get_user_roles(user.id)
        token = create_access_token(
            subject=user.id,
            extra_claims={
                "phone": user.phone,
                "is_phone_verified": user.is_phone_verified,
                "roles": roles,
            },
        )
        return token

    def register_user(
        self,
        phone: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        if not self.user_repo:
            raise RuntimeError("UserRepository is not set on AuthService")

        existing = self.user_repo.get_by_phone(phone)
        if existing:
            raise exceptions.ConflictError("phone already registered")

        if email:
            existing_email = self.user_repo.get_by_email(email)
            if existing_email:
                raise exceptions.ConflictError("email already registered")

        user = User(
            phone=phone,
            email=email,
            full_name=full_name,
            is_active=True,
            is_phone_verified=False,
        )

        if password:
            user.password_hash = hash_password(password)

        created = self.user_repo.create(user)
        return created

    def login(self, phone: str, password: str) -> str:
        if not self.user_repo:
            raise RuntimeError("UserRepository is not set on AuthService")

        user = self.user_repo.get_by_phone(phone)
        if not user:
            raise exceptions.UnauthorizedError("invalid credentials")

        if not user.password_hash:
            raise exceptions.UnauthorizedError("password login not enabled")

        if not verify_password(password, user.password_hash):
            raise exceptions.UnauthorizedError("invalid credentials")

        # <-- here: issue token with roles
        return self._issue_token_with_roles(user)

    def issue_token(self, user: User) -> str:
        """
        Used by OTP flow (we also want roles here)
        """
        return self._issue_token_with_roles(user)

    def ensure_user_by_phone(self, phone: str) -> User:
        if not self.user_repo:
            raise RuntimeError("UserRepository is not set on AuthService")

        user = self.user_repo.get_by_phone(phone)
        if user:
            return user

        new_user = User(
            phone=phone,
            is_active=True,
            is_phone_verified=False,
        )
        return self.user_repo.create(new_user)
