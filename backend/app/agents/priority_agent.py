"""Priority Agent (design doc Section 9.1 step 5 / FR-3).

Scores urgency and maps it to a priority band. Deterministic and explainable:
keyword urgency cues + category weighting. (Kept rule-based so prioritization is
stable and auditable; the LLM-classified category feeds in.)
"""
from __future__ import annotations

from app.agents.base import AgentResult

_URGENT_CUES = ["urgent", "asap", "immediately", "critical", "down", "outage", "cannot work",
                "can't work", "blocked", "production", "security", "breach", "data loss"]
_HIGH_CATEGORIES = {"Network", "Password/Access", "Security"}


class PriorityAgent:
    name = "PriorityAgent"

    def run(self, text: str, category: str | None) -> AgentResult:
        low = text.lower()
        score = 0.3
        cues = [c for c in _URGENT_CUES if c in low]
        score += 0.12 * len(cues)
        if category in _HIGH_CATEGORIES:
            score += 0.15
        score = max(0.0, min(1.0, score))

        if score >= 0.8:
            band = "critical"
        elif score >= 0.6:
            band = "high"
        elif score >= 0.4:
            band = "medium"
        else:
            band = "low"

        return AgentResult(
            self.name, "priority_scored",
            {"priority": band, "priority_score": round(score, 3), "cues": cues},
            confidence=score,
            model_version="rule-based-priority-1.0",
            detail=f"Priority {band} (score={score:.2f}); cues={cues or 'none'}.",
        )
