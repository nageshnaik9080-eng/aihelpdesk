"""Audit log data access (NFR: AI Governance & Auditability)."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog


class LogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        event: str,
        ticket_id: int | None = None,
        actor: str = "system",
        agent_name: str | None = None,
        model_version: str | None = None,
        confidence: float | None = None,
        input_data: Any | None = None,
        output_data: Any | None = None,
    ) -> AuditLog:
        log = AuditLog(
            ticket_id=ticket_id,
            actor=actor,
            event=event,
            agent_name=agent_name,
            model_version=model_version,
            confidence=confidence,
            input_json=json.dumps(input_data, default=str) if input_data is not None else None,
            output_json=json.dumps(output_data, default=str) if output_data is not None else None,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_for_ticket(self, ticket_id: int) -> list[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.ticket_id == ticket_id).order_by(AuditLog.created_at)
        return list(self.db.scalars(stmt))

    def list_recent(self, limit: int = 200) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt))
