"""Analytics endpoint (FR-13; Section 7) — manager/admin only (RBAC)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.security import Role
from app.models import User
from app.schemas import AnalyticsOut
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsOut)
async def get_analytics(
    user: User = Depends(require_roles(Role.HELPDESK_MANAGER, Role.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> AnalyticsOut:
    return AnalyticsService(db).compute()
