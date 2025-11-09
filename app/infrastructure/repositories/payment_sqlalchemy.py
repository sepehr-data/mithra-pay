# app/infrastructure/repositories/payment_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities.payment import Payment
from app.domain.repositories.payment_repository import IPaymentRepository


class SQLAlchemyPaymentRepository(IPaymentRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def list_by_order(self, order_id: int) -> List[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.order_id == order_id)
            .order_by(Payment.id.desc())
            .all()
        )

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
