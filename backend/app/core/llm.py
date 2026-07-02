"""LLM provider abstraction — Gemini only (design doc Section 8.1).

The pipeline calls `llm_complete(...)`. It uses Google Gemini via the
`google-generativeai` SDK. If Gemini is not configured/available or errors, it
returns an `LLMResult` with `available=False` so callers can degrade gracefully
— e.g. fall back to manual routing rather than failing the request
(NFR: Availability / graceful degradation).

The SDK is imported lazily so the backend runs even when `google-generativeai`
is not installed.
"""
from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass

from app.core.config import get_settings

logger = logging.getLogger("helpdesk.llm")
settings = get_settings()

# Hard wall-clock bound so a network/auth hang can never stall a request.
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="gemini")
_GEMINI_TIMEOUT_S = 12

# Once Gemini proves unreachable (bad key, blocked TLS/proxy, etc.) we stop
# retrying for the rest of the process so the pipeline stays snappy in degraded
# mode instead of paying the timeout on every single LLM call.
_gemini_disabled = False


@dataclass
class LLMResult:
    text: str
    provider: str            # "gemini" | "none"
    model: str               # model id used, for AI-governance logging
    available: bool          # False => caller should degrade gracefully


def _call_gemini(prompt: str, system: str | None) -> LLMResult | None:
    global _gemini_disabled
    if not settings.gemini_api_key or _gemini_disabled:
        return None

    def _do() -> str:
        import google.generativeai as genai

        from app.core.tls import genai_transport

        configure_kwargs = {"api_key": settings.gemini_api_key}
        transport = genai_transport()
        if transport:
            configure_kwargs["transport"] = transport
        genai.configure(**configure_kwargs)
        model = genai.GenerativeModel(settings.gemini_model, system_instruction=system or None)
        resp = model.generate_content(prompt, request_options={"timeout": _GEMINI_TIMEOUT_S})
        return (resp.text or "").strip()

    try:
        text = _EXECUTOR.submit(_do).result(timeout=_GEMINI_TIMEOUT_S + 3)
        return LLMResult(text=text, provider="gemini", model=settings.gemini_model, available=True)
    except Exception as exc:  # noqa: BLE001 — degrade on any failure/timeout
        logger.warning("Gemini unavailable (%s); disabling for this process.", exc or "timeout")
        _gemini_disabled = True
        return None


def llm_complete(prompt: str, system: str | None = None) -> LLMResult:
    """Call Gemini. Never raises — returns available=False on failure."""
    result = _call_gemini(prompt, system)
    if result is not None:
        return result
    logger.info("Gemini unavailable; caller should degrade gracefully.")
    return LLMResult(text="", provider="none", model="none", available=False)


def llm_configured() -> bool:
    return bool(settings.gemini_api_key)
