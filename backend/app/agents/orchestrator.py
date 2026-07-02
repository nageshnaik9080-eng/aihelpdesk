"""Agent Orchestrator — runs the exact 12-step ticket lifecycle of design doc
Section 9.1, including duplicate detection, RAG resolution, the confidence check,
and routing/assignment branching.

It mutates the Ticket in place and records every AI decision via the Audit Agent
(NFR: AI Governance). It returns the trace of pipeline steps (for the live AI
processing view, FR-12) and any duplicate suggestions.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from app.agents.audit_agent import AuditAgent
from app.agents.base import AgentResult
from app.agents.duplicate_agent import DuplicateAgent
from app.agents.embedding_agent import EmbeddingAgent
from app.agents.intent_agent import IntentAgent
from app.agents.ocr_agent import OCRAgent
from app.agents.priority_agent import PriorityAgent
from app.agents.rag_agent import RAGAgent
from app.agents.routing_agent import RoutingAgent
from app.agents.vision_agent import VisionAgent
from app.core.config import get_settings
from app.core.vectorstore import upsert_ticket_embedding
from app.models import Ticket
from app.models.ticket import TicketStatus
from app.repositories.article_repo import ArticleRepository
from app.repositories.log_repo import LogRepository
from app.repositories.user_repo import UserRepository

settings = get_settings()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AgentOrchestrator:
    def __init__(self, db) -> None:
        self.db = db
        self.audit = AuditAgent(LogRepository(db))
        self.user_repo = UserRepository(db)
        self.article_repo = ArticleRepository(db)
        self.ocr = OCRAgent()
        self.vision = VisionAgent()
        self.intent = IntentAgent()
        self.priority = PriorityAgent()
        self.embedding = EmbeddingAgent()
        self.duplicate = DuplicateAgent()
        self.rag = RAGAgent()
        self.routing = RoutingAgent()

    def _trace(self, steps: list[dict], result: AgentResult) -> None:
        steps.append({
            "agent": result.agent_name,
            "event": result.event,
            "detail": result.detail,
            "confidence": result.confidence,
        })

    def process(self, ticket: Ticket) -> tuple[list[dict], list[dict]]:
        steps: list[dict] = []
        steps_text = f"{ticket.title}\n{ticket.description}".strip()

        # --- Step 3: OCR + Vision on any attachment ---
        ocr_res = self.ocr.run(ticket.attachment_path)
        self.audit.record(ocr_res, ticket.id)
        self._trace(steps, ocr_res)
        ticket.ocr_text = ocr_res.output.get("text", "")
        if ticket.ocr_text:
            steps_text += "\n" + ticket.ocr_text

        vision_res = self.vision.run(ticket.attachment_path)
        self.audit.record(vision_res, ticket.id)
        self._trace(steps, vision_res)

        # --- Step 4: Intent / category classification ---
        intent_res = self.intent.run(steps_text)
        self.audit.record(intent_res, ticket.id, inputs={"text": steps_text[:500]})
        self._trace(steps, intent_res)
        ticket.category = intent_res.output.get("category")
        ticket.intent = intent_res.output.get("intent")

        # --- Step 5: Priority prediction ---
        prio_res = self.priority.run(steps_text, ticket.category)
        self.audit.record(prio_res, ticket.id)
        self._trace(steps, prio_res)
        ticket.priority = prio_res.output.get("priority")
        ticket.priority_score = prio_res.output.get("priority_score", 0.0)

        # --- Step 6: Duplicate detection (against other open tickets) ---
        dup_res = self.duplicate.run(steps_text, exclude_ticket_id=ticket.id)
        self.audit.record(dup_res, ticket.id)
        self._trace(steps, dup_res)
        suggestions = dup_res.output.get("suggestions", [])

        if dup_res.output.get("is_duplicate"):
            # Step 7 (duplicate branch): suggest/merge and STOP.
            ticket.status = TicketStatus.DUPLICATE
            ticket.duplicate_of_id = dup_res.output.get("duplicate_of_id")
            ticket.first_response_at = _now()
            ticket.routing_reason = dup_res.detail
            self.audit.event(event="stopped_duplicate", ticket_id=ticket.id, detail=dup_res.detail)
            return steps, suggestions

        # Index this ticket so later submissions can detect it as a duplicate.
        upsert_ticket_embedding(ticket.id, steps_text, ticket.status)
        emb_res = self.embedding.run(steps_text)
        self.audit.record(emb_res, ticket.id)
        self._trace(steps, emb_res)

        # --- Step 7: RAG knowledge search + candidate response ---
        rag_res = self.rag.run(steps_text)
        self.audit.record(rag_res, ticket.id)
        self._trace(steps, rag_res)
        sources = rag_res.output.get("sources", [])
        ticket.confidence = rag_res.confidence or 0.0
        for src in sources:
            if src.get("article_id"):
                self.article_repo.increment_retrieval(src["article_id"])

        # --- Step 8: AI Confidence Check ---
        threshold = settings.ai_confidence_threshold
        if ticket.confidence >= threshold and rag_res.output.get("answer"):
            # --- Step 9: High confidence -> auto-resolve ---
            ticket.status = TicketStatus.RESOLVED
            ticket.resolution = rag_res.output["answer"]
            ticket.resolution_source = "auto"
            ticket.kb_sources = json.dumps(sources)
            ticket.first_response_at = _now()
            ticket.resolved_at = _now()
            self.audit.event(
                event="auto_resolved", ticket_id=ticket.id,
                detail=f"Confidence {ticket.confidence:.2f} >= threshold {threshold:.2f}.",
            )
            self._trace(steps, AgentResult(
                "ConfidenceCheck", "auto_resolved",
                detail=f"Auto-resolved (conf {ticket.confidence:.2f} >= {threshold:.2f}).",
                confidence=ticket.confidence,
            ))
        else:
            # --- Step 10: Low confidence -> route to department + assign agent ---
            route_res = self.routing.run(ticket.category, ticket.confidence)
            self.audit.record(route_res, ticket.id)
            self._trace(steps, route_res)
            ticket.department = route_res.output.get("department")
            ticket.routing_reason = route_res.output.get("reason")
            ticket.kb_sources = json.dumps(sources)  # keep AI suggestions for the agent
            ticket.first_response_at = _now()

            agent = self.user_repo.pick_available_agent(ticket.department)
            if agent:
                ticket.assigned_agent_id = agent.id
                ticket.status = TicketStatus.IN_PROGRESS
                self.audit.event(
                    event="assigned_agent", ticket_id=ticket.id,
                    detail=f"Assigned to {agent.email} ({ticket.department}).",
                )
                self._trace(steps, AgentResult(
                    "AssignmentAgent", "assigned_agent",
                    detail=f"Assigned to {agent.full_name or agent.email} in {ticket.department}.",
                ))
            else:
                ticket.status = TicketStatus.ROUTED
                self.audit.event(
                    event="routed_unassigned", ticket_id=ticket.id,
                    detail=f"No available agent in {ticket.department}; left in queue.",
                )

        # Refresh stored embedding with the final status.
        upsert_ticket_embedding(ticket.id, steps_text, ticket.status)
        return steps, suggestions
