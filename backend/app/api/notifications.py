"""In-app notifications (FR-15) — persisted, per-persona, with unread badge.

Managers see manager-targeted notifications (new tickets); employees see their
own (auto-resolutions, escalations). The frontend polls this every 30s.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import Role
from app.models import Notification, User
from app.repositories.notification_repo import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _serialize(n: Notification) -> dict:
    return {
        "id": n.id,
        "type": n.type,
        "message": n.message,
        "ticket_id": n.ticket_id,
        "is_read": n.is_read,
        "recipient_role": n.recipient_role,
        "created_at": n.created_at,
    }


@router.get("")
async def list_notifications(
    user: User = Depends(get_current_user),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    db: Session = Depends(get_db),
):
    """Notifications for the acting persona. Role comes from the resolved user,
    but an explicit `X-User-Role` header (employee|manager) may override it."""
    repo = NotificationRepository(db)
    role = (x_user_role or "").lower()
    if role not in ("manager", "employee"):
        role = "manager" if user.role_name in Role.MANAGER_ROLES else "employee"
    items = repo.list_for_manager() if role == "manager" else repo.list_for_employee(user.email)
    return [_serialize(n) for n in items]


@router.post("/{notification_id}/read")
async def mark_read(notification_id: int, db: Session = Depends(get_db)):
    n = NotificationRepository(db).mark_read(notification_id)
    if n is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found.")
    return {"id": n.id, "is_read": n.is_read}
