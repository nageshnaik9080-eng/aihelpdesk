"""Shared API dependencies — acting-user resolution (public API).

Endpoints are PUBLIC: no token, no OAuth2, no JWT, and no Swagger "Authorize"
button. The persona views (employee / agent / manager) still need to know *who*
is acting, so the acting user is resolved from an optional `X-User-Email` header.
When the header is absent or unknown we fall back to a default demo user so every
endpoint stays usable without any authentication.
"""
from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.repositories.user_repo import UserRepository

# Used when no (or an unknown) X-User-Email header is supplied.
DEFAULT_USER_EMAIL = "employee@demo.com"


def get_current_user(
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the acting user from the optional `X-User-Email` header.

    Falls back to the default demo user, then to the first user in the database.
    Never requires a token — the API is intentionally public.
    """
    repo = UserRepository(db)
    if x_user_email:
        user = repo.get_by_email(x_user_email)
        if user:
            return user
    user = repo.get_by_email(DEFAULT_USER_EMAIL)
    if user:
        return user
    user = db.scalar(select(User).order_by(User.id))
    if user:
        return user
    raise HTTPException(
        status.HTTP_400_BAD_REQUEST,
        "No users exist. Run `python backend/seed.py` to create demo users.",
    )


def require_roles(*roles: str):
    """Dependency factory kept for endpoint compatibility.

    Now that the API is public it is NON-enforcing: it resolves and returns the
    acting user without a 403 role gate. The `roles` argument is retained so
    existing endpoint signatures and intent remain self-documenting.
    """
    _allowed: Iterable[str] = set(roles)  # documentation only; not enforced

    def _checker(user: User = Depends(get_current_user)) -> User:
        return user

    return _checker
