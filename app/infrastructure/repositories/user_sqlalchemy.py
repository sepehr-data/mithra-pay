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

    # ---------- Base ----------

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

    def count_users(self) -> int:
        return self.db.query(User).count()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    # ---------- Roles ----------

    def get_roles(self, user_id: int) -> List[Role]:
        return (
            self.db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all()
        )

    def get_role_names(self, user_id: int) -> List[str]:
        rows = (
            self.db.query(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        return [r[0] for r in rows]

    def ensure_role(self, user_id: int, role_name: str = "user") -> None:

        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise RuntimeError(f"role '{role_name}' not found in roles table")

        exists_link = (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
            .first()
        )
        if exists_link:
            return

        self.db.add(UserRole(user_id=user_id, role_id=role.id))
        self.db.commit()

    def remove_role(self, user_id: int, role_name: str) -> bool:

        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise RuntimeError(f"role '{role_name}' not found in roles table")

        link = (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
            .first()
        )
        if not link:
            return False

        self.db.delete(link)
        self.db.commit()
        return True

    # ---------- Admin helpers ----------

    def set_admin_by_phone(self, phone: str) -> User:

        user = self.get_by_phone(phone)
        if not user:
            raise RuntimeError("user_not_found")

        self.ensure_role(user.id, "admin")
        self.db.refresh(user)
        return user

    def remove_admin_by_phone(self, phone: str) -> User:

        user = self.get_by_phone(phone)
        if not user:
            raise RuntimeError("user_not_found")

        removed = self.remove_role(user.id, "admin")
        if not removed:
            raise RuntimeError("not_admin")

        self.db.refresh(user)
        return user

    def list_admin_users(self, limit: int = 200, offset: int = 0) -> List[User]:

        return (
            self.db.query(User)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .filter(Role.name.in_(["admin", "owner"]))
            .order_by(User.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
