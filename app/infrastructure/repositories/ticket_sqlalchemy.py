# app/infrastructure/repositories/ticket_sqlalchemy.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import case

from app.domain.entities.ticket import Ticket
from app.domain.repositories.ticket_repository import ITicketRepository


class SQLAlchemyTicketRepository(ITicketRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def list(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        q = self.db.query(Ticket)

        if status is not None:
            q = q.filter(Ticket.status == status)

        return (
            q.order_by(
                case(
                    (Ticket.created_at.is_(None), 1),
                    else_=0
                ),
                Ticket.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

