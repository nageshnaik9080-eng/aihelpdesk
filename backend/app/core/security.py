"""Opaque session-token issuance/verification and password hashing (NFR: Security).

Authentication uses random opaque tokens held in an in-memory session table —
deliberately NO JWT and NO OAuth2. Tokens are lost on restart and are not shared
across worker processes (acceptable for this app's scope).

RBAC role constants mirror the personas in design doc Section 2.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory session store: opaque token -> payload ({sub, role, exp, ...}).
_SESSIONS: dict[str, dict[str, Any]] = {}


# --- Personas / roles (design doc Section 2) ---
class Role:
    EMPLOYEE = "employee"
    IT_AGENT = "it_agent"
    ADMIN_AGENT = "admin_agent"           # Administrative Support Agent (HR/Finance/Facilities)
    HELPDESK_MANAGER = "helpdesk_manager"
    KB_ADMIN = "kb_admin"                 # Knowledge Base Administrator
    SYSTEM_ADMIN = "system_admin"

    ALL = {EMPLOYEE, IT_AGENT, ADMIN_AGENT, HELPDESK_MANAGER, KB_ADMIN, SYSTEM_ADMIN}
    # Roles that can work/resolve tickets in a department queue.
    AGENT_ROLES = {IT_AGENT, ADMIN_AGENT}
    # Roles with management/oversight view (analytics, all tickets).
    MANAGER_ROLES = {HELPDESK_MANAGER, SYSTEM_ADMIN}


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    """Issue an opaque random session token and record its payload server-side."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "role": role, "exp": expire}
    if extra:
        payload.update(extra)
    token = secrets.token_urlsafe(32)
    _SESSIONS[token] = payload
    return token


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Look up a session token; return its payload or None if unknown/expired."""
    payload = _SESSIONS.get(token)
    if payload is None:
        return None
    expire = payload.get("exp")
    if isinstance(expire, datetime) and datetime.now(timezone.utc) >= expire:
        _SESSIONS.pop(token, None)
        return None
    return payload


def revoke_access_token(token: str) -> None:
    """Invalidate a session token (e.g. on logout)."""
    _SESSIONS.pop(token, None)
