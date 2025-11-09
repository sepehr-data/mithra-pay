# app/core/config.py
import os
from dotenv import load_dotenv

# load the .env file at project root
load_dotenv()


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-jwt-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    # DB (now this will read your .env values)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "mithra_user")
    DB_PASS: str = os.getenv("DB_PASS", "mithra_pass")
    DB_NAME: str = os.getenv("DB_NAME", "mithrapay")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OTP_EXPIRE_SECONDS: int = int(os.getenv("OTP_EXPIRE_SECONDS", "120"))
    ENV: str = os.getenv("FLASK_ENV", "development")


settings = Settings()
