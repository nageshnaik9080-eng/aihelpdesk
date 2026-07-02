"""Routing Agent (design doc Section 9.1 step 10 / FR-5).

Maps the classified category to the correct department queue (IT / HR / Finance /
Facilities / General). Used when confidence is below the auto-resolution threshold.
"""
from __future__ import annotations

from app.agents.base import AgentResult
from app.models.ticket import Department

_CATEGORY_TO_DEPARTMENT = {
    "Password/Access": Department.IT,
    "Hardware": Department.IT,
    "Software": Department.IT,
    "Network": Department.IT,
    "Email": Department.IT,
    "HR/Payroll": Department.HR,
    "Finance/Reimbursement": Department.FINANCE,
    "Facilities": Department.FACILITIES,
    "Other": Department.GENERAL,
}


class RoutingAgent:
    name = "RoutingAgent"

    def run(self, category: str | None, confidence: float) -> AgentResult:
        department = _CATEGORY_TO_DEPARTMENT.get(category or "Other", Department.GENERAL)
        reason = (
            f"Classified as '{category}' with RAG confidence {confidence:.2f} "
            f"(below auto-resolve threshold) -> routed to {department}."
        )
        return AgentResult(
            self.name, "routed",
            {"department": department, "reason": reason},
            confidence=confidence,
            model_version="routing-map-1.0",
            detail=reason,
        )
