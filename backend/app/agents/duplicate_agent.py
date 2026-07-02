"""Duplicate Agent (design doc Section 9.1 step 6 / FR-4).

Vector-similarity check against existing OPEN tickets. If the top match exceeds
the configured threshold, the new ticket is flagged as a duplicate and the
pipeline stops (suggest/merge), per the workflow.
"""
from __future__ import annotations

from app.agents.base import AgentResult
from app.core.config import get_settings
from app.core.vectorstore import find_similar_tickets

settings = get_settings()


class DuplicateAgent:
    name = "DuplicateAgent"

    def run(self, text: str, exclude_ticket_id: int | None = None) -> AgentResult:
        matches = find_similar_tickets(text, top_k=5, exclude_ticket_id=exclude_ticket_id)
        threshold = settings.duplicate_similarity_threshold
        suggestions = [
            {
                "ticket_id": m["metadata"].get("ticket_id"),
                "title": (m["document"] or "")[:80],
                "similarity": round(m["score"], 3),
            }
            for m in matches
        ]
        top = suggestions[0] if suggestions else None
        is_duplicate = bool(top and top["similarity"] >= threshold)
        return AgentResult(
            self.name,
            "duplicate_checked",
            {
                "is_duplicate": is_duplicate,
                "duplicate_of_id": top["ticket_id"] if is_duplicate else None,
                "suggestions": suggestions,
                "threshold": threshold,
            },
            confidence=top["similarity"] if top else 0.0,
            model_version="vector-cosine-1.0",
            detail=(
                f"Duplicate of #{top['ticket_id']} (sim={top['similarity']:.2f})."
                if is_duplicate else f"No duplicate above {threshold:.2f}."
            ),
        )
