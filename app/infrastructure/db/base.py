# app/infrastructure/db/base.py
from sqlalchemy.orm import declarative_base

# All your models should inherit from this
Base = declarative_base()
