# app/infrastructure/repositories/user_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository

from app.domain.entities.role import Role
from app.domain.entities.user_role import UserRole

class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone == phone).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        return (
            self.db.query(User)
            .order_by(User.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_roles(self, user_id: int) -> List[Role]:
        return (self.db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all())