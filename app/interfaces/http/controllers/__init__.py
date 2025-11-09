# app/interfaces/http/controllers/__init__.py

from app.infrastructure.db.session import SessionLocal


def get_db():
    """
    Returns a new SQLAlchemy session.
    Remember to call db.close() in the controller.
    """
    return SessionLocal()
