"""Notification service (FR-15) — persists in-app notifications + email stub.

Managers get notified when a new ticket lands in a queue; the submitting
employee gets notified when their ticket is auto-resolved or escalated.
Notifications are stored in the `notifications` table and also mirrored to the
audit log so every event stays queryable.
"""
from __future__ import annotations

import logging

from app.models import Ticket
from app.repositories.log_repo import LogRepository
from app.repositories.notification_repo import NotificationRepository

logger = logging.getLogger("helpdesk.notifications")


class NotificationService:
    def __init__(self, db) -> None:
        self.db = db
        self.repo = NotificationRepository(db)
        self.logs = LogRepository(db)

    def _emit(
        self,
        *,
        recipient_role: str,
        type: str,
        message: str,
        ticket_id: int | None = None,
        recipient_email: str | None = None,
    ) -> None:
        self.repo.create(
            recipient_role=recipient_role,
            recipient_email=recipient_email,
            ticket_id=ticket_id,
            type=type,
            message=message,
        )
        self.logs.record(
            event="notification_sent",
            ticket_id=ticket_id,
            actor="NotificationService",
            output_data={"recipient": recipient_email or recipient_role, "type": type, "message": message},
        )
        target = recipient_email or recipient_role
        logger.info("[EMAIL STUB] notification -> %s: %s", target, message)
        print(f"[EMAIL STUB] notification -> {target}: {message}")

    # --- Event helpers (called by TicketService) ---
    def notify_managers_new_ticket(self, ticket: Ticket) -> None:
        message = (
            f"New ticket #{ticket.id}: \"{ticket.title}\" — "
            f"Category: {ticket.category or 'n/a'} | Priority: {ticket.priority or 'n/a'} | "
            f"Dept: {ticket.department or 'unassigned'}"
        )
        self._emit(recipient_role="manager", type="new_ticket", message=message, ticket_id=ticket.id)

    def notify_ticket_resolved(self, ticket: Ticket, recipient_email: str | None) -> None:
        message = (
            f"Your ticket #{ticket.id} \"{ticket.title}\" was automatically resolved. "
            f"See the solution in your dashboard."
        )
        self._emit(
            recipient_role="employee", type="resolved", message=message,
            ticket_id=ticket.id, recipient_email=recipient_email,
        )

    def notify_ticket_escalated(self, ticket: Ticket, recipient_email: str | None) -> None:
        message = (
            f"Your ticket #{ticket.id} \"{ticket.title}\" was escalated to "
            f"{ticket.escalation_target or 'a specialist'} for further investigation."
        )
        self._emit(
            recipient_role="employee", type="escalated", message=message,
            ticket_id=ticket.id, recipient_email=recipient_email,
        )

    def notify_ticket_resolved_by_agent(self, ticket: Ticket, recipient_email: str | None) -> None:
        message = f"Your ticket #{ticket.id} \"{ticket.title}\" was resolved by an agent."
        self._emit(
            recipient_role="employee", type="resolved", message=message,
            ticket_id=ticket.id, recipient_email=recipient_email,
        )
