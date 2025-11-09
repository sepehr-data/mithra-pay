# app/infrastructure/db/maria_engine.py
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from app.core.config import settings


def get_engine():
    # if you ever want sqlite, keep this
    if os.getenv("DB_ENGINE", "").lower() == "sqlite":
        return create_engine("sqlite:///./mithrapay.db", echo=False, future=True)

    url = URL.create(
        drivername="mysql+mysqlconnector",
        username=settings.DB_USER,
        password=settings.DB_PASS,
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        database=settings.DB_NAME,
    )

    # tell the connector to use a collation MariaDB actually has
    engine = create_engine(
        url,
        echo=False,
        future=True,
        connect_args={
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
        },
    )
    return engine
