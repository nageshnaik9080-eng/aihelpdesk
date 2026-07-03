# Interview Q&A Cheat-Sheet — AI Helpdesk Router

> Companion to `PROJECT_DOCUMENTATION.md`. Short, spoken-style answers you can say out loud.
> Grouped by topic. Star (⭐) = very likely to be asked.

---

## A. Project overview

**⭐ Q: Explain your project in 2 minutes.**
> It's a full-stack AI helpdesk router. An employee submits an IT/Admin support ticket in plain English, optionally with a screenshot. A **FastAPI** backend runs the ticket through a **pipeline of agents**: OCR on the image, LLM-based intent classification, rule-based priority scoring, vector-based duplicate detection, and a **RAG** step that searches our knowledge base and asks Gemini to write a grounded answer with a confidence score. If confidence is high, the ticket is **auto-resolved** from the knowledge base; otherwise it's **routed** to the correct human department and escalated. Every decision is logged for governance. The frontend is **React**. Structured data is in **SQLite**; embeddings are in **ChromaDB**.

**Q: Who are the users?**
> Six personas via role-based access: Employee, IT Agent, Admin Agent (HR/Finance/Facilities), Helpdesk Manager, KB Admin, System Admin. Each lands on their own page.

**Q: What problem does it solve?**
> Helpdesks are flooded with repetitive tickets (password resets, VPN issues). This auto-resolves the common ones from a knowledge base and intelligently routes the rest, cutting resolution time and agent workload.

---

## B. RAG (most likely deep-dive)

**⭐ Q: What is RAG and why use it?**
> Retrieval-Augmented Generation. Instead of letting the LLM answer from its training memory — which can hallucinate — I first **retrieve** relevant articles from my own knowledge base, then feed them to the LLM as context and instruct it to answer **only from that context**. This grounds answers in trusted, current company data and lets me cite sources.

**⭐ Q: Walk me through your RAG pipeline end to end.**
> 1) KB articles are **chunked** (sentence-aware, ≤1000 chars, title prepended). 2) Each chunk is **embedded** into a 3072-dim vector by Gemini's embedding model. 3) Vectors are stored in **ChromaDB** in a `kb_chunks` collection. 4) When a ticket arrives, I embed the ticket text and run a **cosine-similarity search** for the top-4 nearest chunks. 5) I build a context block from those chunks and prompt Gemini to return JSON with an `answer` and a `confidence`. 6) I compute a **blended confidence** = `0.6 × LLM confidence + 0.4 × retrieval strength`. 7) The orchestrator decides: high confidence + strong match → auto-resolve; otherwise → route to a human.

**⭐ Q: How does chunking work and why chunk at all?**
> Chunking splits documents so retrieval is precise and fits model limits. Mine is **sentence-aware**: it splits on `. ! ?` and packs whole sentences into ≤1000-char chunks, so a chunk is never cut mid-sentence. I also prepend the article title to the body so a query matching the title still retrieves the article. Most helpdesk articles are short, so they become a single chunk.

**⭐ Q: How do you prevent hallucination?**
> Three ways: (1) a **system instruction** telling Gemini to answer *only* from the provided context and to say so + set low confidence if the context is insufficient; (2) a **retrieval-strength gate** — if the best chunk scores below 0.68 I don't treat it as a real KB match; (3) a **confidence threshold** of 0.70 — below it, I route to a human instead of auto-resolving.

**Q: What's the confidence score and how is it computed?**
> It's how sure we are the auto-answer is correct. I blend two signals: the LLM's own self-assessed confidence (weight 0.6) and the retrieval strength — the top chunk's similarity score (weight 0.4). This stops me trusting the LLM alone, and stops me auto-resolving on a weak match.

**Q: What are the actual thresholds?**
> `kb_match_min_score = 0.68` (is this a real match?), `ai_confidence_threshold = 0.70` (auto-resolve gate), duplicate merge `0.90`, duplicate suggest `0.85`. All configurable via environment variables — nothing hardcoded.

**Q: Where do the "documents" come from? Do you parse PDFs?**
> No file parsing. My knowledge base is 30 curated, structured articles (Title/Category/Issue/Solution) defined in `backend/kb_articles.py`. A seed script writes them into SQLite and embeds them into ChromaDB. KB admins can also add/edit articles at runtime through the UI, which re-embeds automatically.

---

## C. Embeddings & vectors

**⭐ Q: What is an embedding?**
> A list of numbers — a vector — that represents the *meaning* of text. Texts with similar meaning get vectors pointing in similar directions, so I can measure semantic similarity mathematically.

**⭐ Q: What is cosine similarity?**
> A measure of the angle between two vectors, from −1 to 1. 1 means same direction = very similar meaning. Since I L2-normalize my vectors, cosine similarity is just their dot product — fast to compute.

**Q: Which embedding model, and what dimension?**
> Google's `gemini-embedding-001`, 3072 dimensions. I also use **task types**: `RETRIEVAL_DOCUMENT` for KB chunks, `RETRIEVAL_QUERY` for the search query, and `SEMANTIC_SIMILARITY` for ticket-vs-ticket duplicate checks — this improves accuracy because the model optimizes the vector for the specific job.

**Q: What if the embedding API is down?**
> The backend is chosen once at startup with retries: Gemini first, then local `sentence-transformers`, then a deterministic **hashing fallback**. If a call fails after retries it returns a **zero vector** (cosine 0 with everything, so no false match) rather than corrupting the index with a wrong-dimension vector. And if only the non-semantic hashing backend is active, I **disable duplicate detection** so it can't produce false positives.

---

## D. ChromaDB / vector database

**⭐ Q: What is ChromaDB and why not just use SQL?**
> ChromaDB is an open-source **vector database** built for nearest-neighbor search over embeddings. A relational DB is great for exact lookups and joins, but finding the "most semantically similar" rows means comparing a query vector to every stored vector — that's exactly what a vector DB is optimized for. So I use SQLite for structured data and ChromaDB for similarity search.

**Q: How is ChromaDB organized here?**
> Two collections: `kb_chunks` (knowledge base vectors for RAG) and `ticket_embeddings` (open-ticket vectors for duplicate detection). It's persisted to disk under `data/chroma/`.

**Q: ChromaDB returns distance, but you use a score — how?**
> ChromaDB returns a squared-L2 distance for normalized vectors. I convert it to a cosine-like similarity in [0,1] with `score = max(0, 1 − distance/2)`, so higher always means more similar.

**Q: What's the NumPy fallback?**
> If ChromaDB can't load on a given Python build, the vector store transparently falls back to a small NumPy cosine store persisted as JSON. Same behavior, so RAG and duplicate detection work anywhere.

---

## E. Multi-agent architecture

**⭐ Q: Why call them "agents"? What are they?**
> Each agent is a small class with one responsibility that returns a uniform `AgentResult` (event, output, confidence, model version). An **orchestrator** runs them in sequence and makes the final decision. It's a clean separation-of-concerns pattern — each step is independently testable and auditable.

**Q: List the agents.**
> OCRAgent, IntentAgent, PriorityAgent, DuplicateAgent, RAGAgent, RoutingAgent, and AuditAgent (which logs every step). The AgentOrchestrator coordinates them.

**Q: Which agents use the LLM vs rules?**
> IntentAgent and RAGAgent use the LLM (Gemini). PriorityAgent and RoutingAgent are **rule-based** on purpose — priority and routing must be stable, explainable, and auditable. IntentAgent has a keyword fallback if the LLM is down.

**Q: How does duplicate detection work?**
> I embed the new ticket and search the `ticket_embeddings` collection. Two tiers: similarity ≥ 0.90 → auto-merge (and if the original is already resolved, reuse its resolution); 0.85–0.90 → show as "possibly related" and continue to RAG; below → ignore.

---

## F. FastAPI / backend

**⭐ Q: Why FastAPI?**
> It's async (scales well for I/O like LLM calls), has automatic request validation via Pydantic, and auto-generates Swagger docs at `/docs`. It's modern and fast.

**Q: Explain your layering.**
> API routers (HTTP only) → Services (business logic) → Agents (AI) / Repositories (data access) → Models (tables). Each layer has one job, so I can change the AI logic without touching HTTP code, etc.

**Q: What's dependency injection here?**
> FastAPI's `Depends`. For example `Depends(get_db)` yields a scoped DB session per request, and `Depends(get_current_user)` resolves the acting user. It keeps endpoints clean and testable.

**Q: How does auth work?**
> This MVP is intentionally simple: the API is public and the acting persona is passed via an `X-User-Email` header. There's password hashing (bcrypt) and opaque in-memory session tokens available, but no JWT/OAuth2 — a deliberate scope choice for a demo. Role checks exist in code but aren't hard-enforced.

**Q: What's idempotency and why do you have it?**
> An optional idempotency key on submission. If the same request is retried (e.g. network glitch), I return the existing ticket instead of re-running the expensive AI pipeline. It prevents duplicate work and duplicate tickets.

---

## G. Frontend

**Q: How is the frontend structured?**
> React + Vite. `react-query` manages all server data (fetching, caching, refetching). One axios client attaches the user header to every call. Routing is role-based — each persona gets guarded routes and their own landing page. MUI for components.

**Q: How does the UI stay in sync after an action?**
> react-query cache invalidation. E.g. after submitting or resolving a ticket, I invalidate the `['tickets']` query key, which triggers an automatic refetch so the list updates without manual state juggling.

---

## H. Curveballs / "why" questions

**⭐ Q: What happens if Gemini is completely unavailable?**
> The app degrades gracefully and never crashes: intent classification falls back to a keyword classifier, RAG returns confidence 0 so the ticket routes to a human, and embeddings fall back to sentence-transformers or a hashing store (with duplicate detection disabled to avoid false matches). Nothing hard-fails on an AI outage.

**Q: Why SQLite and ChromaDB instead of one database?**
> Different jobs. Relational data — users, tickets, relationships, transactions — belongs in a relational DB. Similarity search over embeddings belongs in a vector DB. Using each for its strength keeps both simple and fast.

**Q: Why not LangChain?**
> My pipeline is small and specific. Hand-writing it keeps dependencies light, makes the control flow fully transparent, and makes debugging trivial. The trade-off is a bit more code, but I keep full control and there's no framework magic to fight.

**Q: How would you scale this to production?**
> Swap SQLite for Postgres, run a managed/clustered ChromaDB (or pgvector), move sessions to Redis, add real JWT auth + enforced RBAC, put LLM calls behind a queue with rate limiting and caching, add batch embedding, and add monitoring on the auto-resolution rate and confidence distribution.

**Q: How do you know the AI is doing a good job? (metrics)**
> The analytics service computes auto-resolution rate, routing accuracy, average resolution & first-response time, escalation rate, and CSAT from thumbs-up/down feedback. A thumbs-down on an AI resolution auto-re-escalates to a human — so bad answers get caught and corrected.

**Q: What was the hardest bug / a real design fix?**
> Early on, the hashing-fallback embedder produced near-random vectors that caused **false duplicate matches** (74–88% "similarity" between unrelated tickets). I fixed it by (a) making the backend resolve to real Gemini embeddings with retries so a transient timeout doesn't lock it into hashing, and (b) disabling duplicate detection entirely whenever only the non-semantic backend is active.

**Q: What would you improve given more time?**
> Enforce RBAC properly, add automated tests around the decision thresholds, support real document ingestion (PDF/Markdown) into the KB, add streaming LLM responses in the UI, and A/B test the confidence-blend weights.

---

## I. 30-second closer

> "The theme of the whole codebase is **grounded, governed, and graceful**: RAG grounds answers in a real knowledge base with citations; every agent decision is audited for governance; and every AI component degrades gracefully so the system stays up even when the LLM, the embedder, or the vector DB isn't available."
