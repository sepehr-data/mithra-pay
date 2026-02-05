# app/infrastructure/repositories/banner_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import case

from app.domain.entities.banner import Banner
from app.domain.repositories.banner_repository import IBannerRepository


class SQLAlchemyBannerRepository(IBannerRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, banner_id: int) -> Optional[Banner]:
        return self.db.query(Banner).filter(Banner.id == banner_id).first()

    def list(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Banner]:
        q = self.db.query(Banner)

        if status is not None:
            q = q.filter(Banner.status == status)

        return (
            q.order_by(
                case(
                    (Banner.created_at.is_(None), 1),
                    else_=0
                ),
                Banner.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, banner: Banner) -> Banner:
        self.db.add(banner)
        self.db.commit()
        self.db.refresh(banner)
        return banner

    def update(self, banner: Banner) -> Banner:
        self.db.add(banner)
        self.db.commit()
        self.db.refresh(banner)
        return banner

    def delete(self, banner_id: int) -> None:
        banner = self.get_by_id(banner_id)
        if not banner:
            return

        self.db.delete(banner)
        self.db.commit()
