"""OCR Agent (design doc Section 8.2.1 / FR-11, Should-priority).

Extracts text from uploaded screenshots. Real OCR uses pytesseract, which needs
the Tesseract binary installed system-wide. When it is unavailable this agent
degrades to a no-op stub while keeping the pipeline step correct — exactly the
graceful-degradation behavior required by the NFRs.
"""
from __future__ import annotations

import logging

from app.agents.base import AgentResult

logger = logging.getLogger("helpdesk.agents.ocr")


class OCRAgent:
    name = "OCRAgent"

    def run(self, attachment_path: str | None) -> AgentResult:
        if not attachment_path:
            return AgentResult(self.name, "ocr_skipped", {"text": ""}, detail="No attachment provided.")

        text = self._extract(attachment_path)
        backend = "pytesseract" if text else "stub"
        return AgentResult(
            self.name,
            "ocr_extracted",
            {"text": text, "backend": backend},
            model_version=backend,
            detail=f"Extracted {len(text)} chars via {backend}.",
        )

    @staticmethod
    def _extract(path: str) -> str:
        try:
            import pytesseract
            from PIL import Image

            return pytesseract.image_to_string(Image.open(path)).strip()
        except Exception as exc:  # noqa: BLE001 — stub fallback
            logger.info("OCR unavailable (%s); returning empty extraction (stub).", exc)
            return ""
