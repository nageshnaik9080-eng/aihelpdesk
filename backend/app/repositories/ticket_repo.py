"""Ticket data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ticket
from app.models.ticket import TicketStatus


class TicketRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, ticket_id: int) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def get_by_idempotency_key(self, key: str) -> Ticket | None:
        return self.db.scalar(select(Ticket).where(Ticket.idempotency_key == key))

    def add(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def save(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def list_for_employee(self, employee_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.employee_id == employee_id).order_by(Ticket.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_for_department(self, department: str) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.department == department).order_by(Ticket.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_for_agent(self, agent_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.assigned_agent_id == agent_id).order_by(Ticket.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_all(self) -> list[Ticket]:
        return list(self.db.scalars(select(Ticket).order_by(Ticket.created_at.desc())))

    def list_open(self) -> list[Ticket]:
        open_states = (TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.ROUTED, TicketStatus.ESCALATED)
        return list(self.db.scalars(select(Ticket).where(Ticket.status.in_(open_states))))
