"""Notification data access (FR-15)."""
from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        recipient_role: str,
        type: str,
        message: str,
        ticket_id: int | None = None,
        recipient_email: str | None = None,
    ) -> Notification:
        n = Notification(
            recipient_role=recipient_role,
            recipient_email=recipient_email,
            ticket_id=ticket_id,
            type=type,
            message=message,
        )
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def list_for_manager(self, limit: int = 100) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.recipient_role == "manager")
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def list_for_employee(self, email: str, limit: int = 100) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(
                Notification.recipient_role == "employee",
                or_(Notification.recipient_email == email, Notification.recipient_email.is_(None)),
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def mark_read(self, notification_id: int) -> Notification | None:
        n = self.db.get(Notification, notification_id)
        if n is None:
            return None
        n.is_read = True
        self.db.commit()
        self.db.refresh(n)
        return n
