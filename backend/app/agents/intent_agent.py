"""Intent Agent (design doc Section 8.2.1 / FR-1, FR-2, FR-3).

Classifies category + intent and produces a classification confidence. Uses the
LLM provider when available; falls back to a deterministic keyword classifier so
classification still works when no LLM is configured (NFR: graceful degradation).
"""
from __future__ import annotations

from app.agents.base import AgentResult, extract_json
from app.core.llm import llm_complete

# Canonical categories the router understands (kept single-language per Section 6).
CATEGORIES = [
    "Password/Access", "Hardware", "Software", "Network", "Email",
    "HR/Payroll", "Finance/Reimbursement", "Facilities", "Other",
]

# Keyword cues for the deterministic fallback classifier.
_KEYWORDS: dict[str, list[str]] = {
    "Password/Access": ["password", "reset", "locked", "login", "mfa", "2fa", "access", "vpn account"],
    "Hardware": ["laptop", "monitor", "keyboard", "mouse", "printer", "battery", "charger", "device", "screen broken"],
    "Software": ["install", "license", "application", "app crash", "software", "update", "excel", "outlook crash"],
    "Network": ["wifi", "wi-fi", "internet", "network", "vpn", "connection", "slow connection"],
    "Email": ["email", "mailbox", "outlook", "spam", "distribution list", "calendar invite"],
    "HR/Payroll": ["leave", "payroll", "salary", "hr", "benefits", "onboarding", "offboarding", "payslip"],
    "Finance/Reimbursement": ["reimbursement", "invoice", "expense", "finance", "payment", "budget", "claim"],
    "Facilities": ["desk", "chair", "ac", "air conditioning", "office", "parking", "badge", "room booking"],
}

_SYSTEM = "You are an IT/Admin helpdesk classification agent. Respond with JSON only."


class IntentAgent:
    name = "IntentAgent"

    def run(self, text: str) -> AgentResult:
        llm = self._classify_llm(text)
        if llm is not None:
            return llm
        return self._classify_rules(text)

    def _classify_llm(self, text: str) -> AgentResult | None:
        prompt = (
            "Classify the support ticket below.\n"
            f"Allowed categories: {', '.join(CATEGORIES)}.\n"
            "Return JSON: {\"category\": <one allowed category>, "
            "\"intent\": <short verb phrase>, \"confidence\": <0..1 float>}\n\n"
            f"Ticket:\n{text}"
        )
        result = llm_complete(prompt, system=_SYSTEM)
        if not result.available:
            return None
        data = extract_json(result.text) or {}
        category = data.get("category") if data.get("category") in CATEGORIES else "Other"
        confidence = float(data.get("confidence", 0.6) or 0.6)
        return AgentResult(
            self.name, "intent_classified",
            {"category": category, "intent": data.get("intent", "support_request")},
            confidence=max(0.0, min(1.0, confidence)),
            model_version=f"{result.provider}:{result.model}",
            detail=f"LLM classified as {category}.",
        )

    def _classify_rules(self, text: str) -> AgentResult:
        low = text.lower()
        scores = {cat: sum(1 for kw in kws if kw in low) for cat, kws in _KEYWORDS.items()}
        best_cat, best_score = max(scores.items(), key=lambda kv: kv[1])
        if best_score == 0:
            best_cat, confidence = "Other", 0.3
        else:
            total = sum(scores.values())
            confidence = min(0.7, 0.4 + 0.1 * best_score) if total else 0.3
        return AgentResult(
            self.name, "intent_classified",
            {"category": best_cat, "intent": f"{best_cat.lower()}_request"},
            confidence=confidence,
            model_version="rule-based-fallback",
            detail=f"Rule-based classification: {best_cat} (score={best_score}).",
        )
