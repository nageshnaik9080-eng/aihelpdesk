"""Ticket and KnowledgeArticle entities (design doc Sections 9 & 10).

The Ticket row records the full output of the 12-step workflow so the lifecycle
is auditable and trackable in real time (FR-12).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# --- Ticket lifecycle states (design doc Section 3.8) ---
class TicketStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ROUTED = "routed"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    DUPLICATE = "duplicate"


class Department:
    IT = "IT"
    HR = "HR"
    FINANCE = "Finance"
    FACILITIES = "Facilities"
    GENERAL = "General"
    ALL = {IT, HR, FINANCE, FACILITIES, GENERAL}


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Raw submission
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    attachment_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ocr_text: Mapped[str] = mapped_column(Text, default="")          # FR-11

    # AI pipeline outputs (FR-1..FR-3)
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)   # low/medium/high/critical
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Resolution / routing (FR-5..FR-10)
    status: Mapped[str] = mapped_column(String(20), default=TicketStatus.OPEN, index=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_source: Mapped[str | None] = mapped_column(String(20), nullable=True)  # auto|agent
    kb_sources: Mapped[str | None] = mapped_column(Text, nullable=True)               # JSON list of citations
    department: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    assigned_agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    duplicate_of_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id"), nullable=True)
    escalation_target: Mapped[str | None] = mapped_column(String(50), nullable=True)  # L2/L3/vendor
    routing_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Idempotency (NFR: Reliability) — same key never runs the AI pipeline twice.
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)

    # Timestamps for KPIs (Section 7)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    first_response_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class KnowledgeArticle(Base):
    """KB article; its chunks are embedded into ChromaDB for RAG (FR-6/FR-7)."""
    __tablename__ = "knowledge_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="General")
    retrieval_count: Mapped[int] = mapped_column(Integer, default=0)  # KB utilization (Section 7)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
