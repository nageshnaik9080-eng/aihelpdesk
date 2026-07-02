"""Audit Agent (design doc Section 5: AI Governance & Auditability).

Persists a structured, queryable record of every agent decision — agent name,
model/version, confidence, and input/output — to the audit_logs table.
"""
from __future__ import annotations

from app.agents.base import AgentResult
from app.repositories.log_repo import LogRepository


class AuditAgent:
    name = "AuditAgent"

    def __init__(self, log_repo: LogRepository) -> None:
        self.log_repo = log_repo

    def record(self, result: AgentResult, ticket_id: int | None, inputs: dict | None = None) -> None:
        self.log_repo.record(
            event=result.event,
            ticket_id=ticket_id,
            actor=result.agent_name,
            agent_name=result.agent_name,
            model_version=result.model_version,
            confidence=result.confidence,
            input_data=inputs,
            output_data=result.output,
        )

    def event(self, *, event: str, ticket_id: int | None, actor: str = "system",
              detail: str | None = None) -> None:
        """Record a non-agent lifecycle event (e.g. escalation, manual resolve)."""
        self.log_repo.record(
            event=event, ticket_id=ticket_id, actor=actor,
            output_data={"detail": detail} if detail else None,
        )
