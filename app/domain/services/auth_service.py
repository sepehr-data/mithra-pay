# app/domain/services/auth_service.py
from typing import Optional

from app.core import exceptions
from app.core.security import hash_password, verify_password, create_access_token
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository


class AuthService:
    """
    Handles register/login and token issuing.
    This service needs a concrete IUserRepository injected.
    """

    def __init__(self, user_repo: IUserRepository | None = None):
        # in real app, inject from DI container
        self.user_repo = user_repo

    # --- helper to set repo afterwards (if you construct without args)
    def set_user_repo(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def register_user(
        self,
        phone: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        if not self.user_repo:
            raise RuntimeError("UserRepository is not set on AuthService")

        # check uniqueness
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
        """
        password-based login.
        """
        if not self.user_repo:
            raise RuntimeError("UserRepository is not set on AuthService")

        user = self.user_repo.get_by_phone(phone)
        if not user:
            raise exceptions.UnauthorizedError("invalid credentials")

        if not user.password_hash:
            raise exceptions.UnauthorizedError("password login not enabled")

        if not verify_password(password, user.password_hash):
            raise exceptions.UnauthorizedError("invalid credentials")

        token = create_access_token(
            subject=user.id,
            extra_claims={"phone": user.phone, "is_phone_verified": user.is_phone_verified},
        )
        return token

    def issue_token(self, user: User) -> str:
        """
        Used by OTP flow
        """
        token = create_access_token(
            subject=user.id,
            extra_claims={"phone": user.phone, "is_phone_verified": user.is_phone_verified},
        )
        return token

    def ensure_user_by_phone(self, phone: str) -> User:
        """
        If user with this phone exists, return it. Otherwise create a simple one.
        Useful for OTP-only flows.
        """
        if not self.user_repo:
            raise RuntimeError("UserRepository is not set on AuthService")

        user = self.user_repo.get_by_phone(phone)
        if user:
            return user

        # create minimal user
        new_user = User(
            phone=phone,
            is_active=True,
            is_phone_verified=False,
        )
        return self.user_repo.create(new_user)
