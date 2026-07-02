"""Vision Agent (design doc Section 8.2.1) — analyzes visual content of attachments.

MVP-light: records basic image metadata as additional context. Designed as a
clean extension point for a multimodal LLM later (kept out of MVP-Must scope).
"""
from __future__ import annotations

import logging

from app.agents.base import AgentResult

logger = logging.getLogger("helpdesk.agents.vision")


class VisionAgent:
    name = "VisionAgent"

    def run(self, attachment_path: str | None) -> AgentResult:
        if not attachment_path:
            return AgentResult(self.name, "vision_skipped", {"context": ""}, detail="No attachment.")
        try:
            from PIL import Image

            with Image.open(attachment_path) as img:
                context = f"Image attachment {img.width}x{img.height}, format={img.format}."
        except Exception as exc:  # noqa: BLE001
            logger.info("Vision analysis unavailable (%s).", exc)
            context = "Attachment present (visual analysis unavailable)."
        return AgentResult(self.name, "vision_analyzed", {"context": context}, detail=context)
