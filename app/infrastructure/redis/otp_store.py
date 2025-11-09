# app/infrastructure/redis/otp_store.py
import random
from app.core.config import settings
from .redis_client import redis_client


class OTPStore:
    """
    Small helper around Redis for OTPs.
    Key format: otp:{phone}
    """

    def __init__(self, ttl: int | None = None):
        self.ttl = ttl or settings.OTP_EXPIRE_SECONDS

    def generate_code(self, length: int | None = None) -> str:
        length = length or settings.OTP_LENGTH
        return "".join(str(random.randint(0, 9)) for _ in range(length))

    def set_code(self, phone: str, code: str):
        key = f"otp:{phone}"
        redis_client.setex(key, self.ttl, code)

    def verify_code(self, phone: str, code: str) -> bool:
        key = f"otp:{phone}"
        saved = redis_client.get(key)
        if not saved:
            return False
        if saved.decode() == code:
            # consume it
            redis_client.delete(key)
            return True
        return False
