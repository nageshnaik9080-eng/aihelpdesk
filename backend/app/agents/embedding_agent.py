"""Embedding Agent (design doc Section 8.2.1).

Generates vector embeddings for tickets and KB documents. Thin wrapper around
app.core.embeddings so the active backend is reported for audit logging.
"""
from __future__ import annotations

from app.agents.base import AgentResult
from app.core.embeddings import embed, embedding_backend


class EmbeddingAgent:
    name = "EmbeddingAgent"

    def run(self, text: str) -> AgentResult:
        vector = embed(text)
        return AgentResult(
            self.name, "embedded",
            {"dim": len(vector)},
            model_version=embedding_backend(),
            detail=f"Embedded text into {len(vector)}-d vector ({embedding_backend()}).",
        )
