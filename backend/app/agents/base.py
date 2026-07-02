"""Shared agent primitives."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

# Bump when agent logic changes — recorded in audit logs for AI governance.
AGENT_SUITE_VERSION = "agents-1.0.0"


@dataclass
class AgentResult:
    """Normalized output every agent returns, so the orchestrator can audit uniformly."""
    agent_name: str
    event: str
    output: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None
    model_version: str = AGENT_SUITE_VERSION
    detail: str = ""


def extract_json(text: str) -> dict[str, Any] | None:
    """Best-effort extraction of a JSON object from an LLM response."""
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
