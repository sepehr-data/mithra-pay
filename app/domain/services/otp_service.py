# app/domain/services/otp_service.py
from app.infrastructure.redis.otp_store import OTPStore
from app.domain.services.auth_service import AuthService
from app.core import exceptions
from app.domain.repositories.user_repository import IUserRepository


class OTPService:
    """
    High-level OTP flow:
    - send_otp(phone)
    - verify_otp_and_issue_token(phone, code)
    """

    def __init__(
        self,
        user_repo: IUserRepository | None = None,
        otp_store: OTPStore | None = None,
    ):
        self.otp_store = otp_store or OTPStore()
        self.auth_service = AuthService(user_repo=user_repo)

    def send_otp(self, phone: str) -> str:
        """
        Generate + store OTP. (Integrate with SMS gateway here.)
        Returns code for debug/dev.
        """
        code = self.otp_store.generate_code()
        self.otp_store.set_code(phone, code)
        # TODO: integrate with SMS provider
        return code

    def verify_otp_and_issue_token(self, phone: str, code: str) -> str:
        ok = self.otp_store.verify_code(phone, code)
        if not ok:
            raise exceptions.UnauthorizedError("invalid or expired otp")

        # ensure user exists
        user = self.auth_service.ensure_user_by_phone(phone)
        # mark verified? -> you can update user here via repo
        user.is_phone_verified = True
        # persist this change
        if self.auth_service.user_repo:
            self.auth_service.user_repo.update(user)

        token = self.auth_service.issue_token(user)
        return token
