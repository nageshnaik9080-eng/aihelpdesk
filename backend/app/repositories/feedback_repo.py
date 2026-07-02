"""Feedback data access (FR-14)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Feedback


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, feedback: Feedback) -> Feedback:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def list_for_ticket(self, ticket_id: int) -> list[Feedback]:
        return list(self.db.scalars(select(Feedback).where(Feedback.ticket_id == ticket_id)))

    def all(self) -> list[Feedback]:
        return list(self.db.scalars(select(Feedback)))
