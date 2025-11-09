# app/infrastructure/db/session.py
from sqlalchemy.orm import sessionmaker, Session
from app.infrastructure.db.maria_engine import get_engine

# Create the engine once
engine = get_engine()

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Session:
    """
    Dependency-style helper (useful in Flask views or services):
    with get_db() as db:
        ...
    or in Flask, call inside request and close afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
