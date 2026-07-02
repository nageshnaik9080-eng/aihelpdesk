"""Notification entity (FR-15) — persisted in-app notifications.

Managers are notified when a new ticket is routed to a queue; the submitting
employee is notified when their ticket is auto-resolved or escalated. The
frontend polls `GET /notifications` and shows an unread badge.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 'manager' => broadcast to manager/admin personas; 'employee' => a specific person.
    recipient_role: Mapped[str] = mapped_column(String(20), index=True)
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    ticket_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(30))  # new_ticket | resolved | escalated | routed | closed
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
