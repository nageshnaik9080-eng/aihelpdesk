# AI-Powered IT/Admin Helpdesk Router — Complete Project Documentation

> A full, interview-ready walkthrough of the entire codebase: architecture, every important
> file, the multi-agent + RAG pipeline, how embeddings/ChromaDB/FastAPI work, and the exact
> request→response flow from frontend to backend and back.

---

## 0. Read this first — two myths to clear up

Before anything else, two things people often assume about this project that are **wrong**:

| Myth | Reality in this project |
|------|-------------------------|
| "It uses MongoDB." | ❌ **No MongoDB.** Structured data (users, tickets, KB articles, feedback, audit logs) lives in **SQLite** — a single file `data/helpdesk.db` — accessed through **SQLAlchemy** (an ORM). Vectors live in **ChromaDB** (`data/chroma/`). |
| "It uses LangChain." | ❌ **No LangChain.** The RAG pipeline is **written by hand**. It calls the **Google Gemini** API directly (via the `google-genai` SDK) and talks to **ChromaDB** directly. No orchestration framework. |
| "Documents are uploaded/parsed from PDF/Word files." | ❌ The knowledge base is **structured Python data** in `backend/kb_articles.py` (30 articles, KB001–KB030). A seed script writes them into SQLite and embeds them into ChromaDB. There is no file-parsing step. |

If the interviewer says "so your RAG reads PDFs," the honest answer is: *"No — my knowledge base is a curated set of structured articles stored in a relational DB; those articles are chunked and embedded into a vector database for retrieval."*

---

## 1. What the project is (elevator pitch)

An **AI helpdesk router**. An employee submits an IT/Admin support ticket in plain English (optionally with a screenshot). A **pipeline of small "agents"** automatically:

1. Reads any screenshot text (OCR).
2. Classifies the ticket (category + intent).
3. Scores urgency (priority).
4. Checks whether it's a **duplicate** of an existing ticket.
5. Runs **RAG** (Retrieval-Augmented Generation): searches the knowledge base and asks an LLM to write a grounded answer, with a confidence score.
6. **Decides**: if confidence is high → auto-resolve with the KB answer; otherwise → route to the correct human department (IT / HR / Finance / Facilities) and escalate.

Everything each agent does is **logged** (audit trail) for AI governance. Managers see **analytics** (auto-resolution rate, CSAT, etc.). It's a full-stack app: **FastAPI** backend + **React** frontend.

---

## 2. Technology stack & key library definitions

### Backend (Python)

| Library | What it is (simple) | How this project uses it |
|---------|--------------------|--------------------------|
| **FastAPI** | A modern Python web framework for building APIs. Fast, async, auto-generates Swagger docs. | Defines all HTTP endpoints (`/tickets`, `/kb`, `/auth`, …). Entry point: `backend/app/main.py`. |
| **Uvicorn** | An ASGI web server — the process that actually runs the FastAPI app and listens on a port. | Runs the backend: `uvicorn app.main:app`. |
| **SQLAlchemy** | An **ORM** (Object-Relational Mapper): lets you work with database rows as Python objects instead of raw SQL. | Defines tables (`User`, `Ticket`, `KnowledgeArticle`, …) and runs queries. |
| **SQLite** | A tiny, file-based relational database (no server needed). | Stores all structured data in `data/helpdesk.db`. |
| **Pydantic** | Data-validation library. Defines "schemas" (typed shapes) and validates request/response bodies. | `backend/app/schemas.py` — every API input/output is a Pydantic model. |
| **pydantic-settings** | Loads config from environment variables / `.env` files into a typed object. | `backend/app/core/config.py`. |
| **ChromaDB** | An open-source **vector database** — stores embeddings and does similarity search. | Stores KB chunk vectors and ticket vectors; powers RAG + duplicate detection. |
| **google-genai** | Google's official SDK for the **Gemini** models (LLM + embeddings). | Generates answers (`gemini-2.5-flash-lite`) and embeddings (`gemini-embedding-001`). |
| **NumPy** | Numerical arrays / linear algebra. | Cosine-similarity math in the fallback vector store. |
| **passlib + bcrypt** | Password hashing. | Hashes demo user passwords securely. |
| **httpx** | Async HTTP client. | Used under the hood by `google-genai`; also for TLS control. |

### Frontend (JavaScript)

| Library | What it is | How this project uses it |
|---------|-----------|--------------------------|
| **React** | UI library for building component-based interfaces. | The entire SPA (single-page app). |
| **Vite** | Fast build tool / dev server for modern JS. | Runs and bundles the frontend (`npm run dev`). |
| **React Router** | Client-side routing (URL → page component). | `App.jsx` maps `/employee`, `/agent`, `/manager`, etc. |
| **@tanstack/react-query** | Server-state management: fetching, caching, refetching data. | All API calls go through `useQuery`/`useMutation` hooks. |
| **MUI (Material UI)** | Ready-made React component library (buttons, tables, chips). | All UI styling/components. |
| **axios** | Promise-based HTTP client. | The single API client (`src/api/client.js`). |

### Key AI/ML concepts (plain definitions)

- **Embedding**: a list of numbers (a *vector*, here 3072-dimensional for Gemini) that represents the *meaning* of a piece of text. Texts with similar meaning have vectors that point in similar directions.
- **Vector database (ChromaDB)**: a database optimized for storing embeddings and finding the *nearest* vectors to a query vector.
- **Cosine similarity**: a number (−1 to 1) measuring how aligned two vectors are. 1 = same direction (very similar meaning). This is how "closeness" is measured.
- **RAG (Retrieval-Augmented Generation)**: instead of asking an LLM to answer from memory (which can hallucinate), you first **retrieve** relevant documents from your own knowledge base, then feed them to the LLM as *context* and ask it to answer **only from that context**. This "grounds" the answer in real, trusted data.
- **LLM (Large Language Model)**: here, Google **Gemini**. Used for (a) classifying tickets and (b) writing the grounded RAG answer.
- **Chunking**: splitting a document into smaller pieces before embedding, so retrieval is precise and fits model limits.

---

## 3. High-level architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + Vite)                       │
│  Pages: Login / Employee / Agent / Manager / KB / Escalations / DB    │
│  Data layer: react-query hooks  ─────►  axios client (X-User-Email)   │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │ HTTP (JSON / multipart)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI, app/main.py)                    │
│                                                                        │
│  API routers  ─►  Services  ─►  Agent Orchestrator  ─►  Agents        │
│  (app/api)        (app/services)  (app/agents/orchestrator.py)         │
│                                        │                               │
│                    ┌───────────────────┼───────────────────┐          │
│                    ▼                   ▼                   ▼          │
│           SQLite (SQLAlchemy)   ChromaDB (vectors)   Gemini API        │
│           data/helpdesk.db      data/chroma/        (LLM + embeddings) │
└─────────────────────────────────────────────────────────────────────┘
```

**Layered design (why it's clean):**

- **API layer** (`app/api/*`) — thin. Only handles HTTP: parse request, call a service, return a response.
- **Service layer** (`app/services/*`) — business logic (submission, lifecycle, analytics, KB CRUD).
- **Agent layer** (`app/agents/*`) — the AI pipeline (one class per responsibility).
- **Core layer** (`app/core/*`) — infrastructure: DB, config, LLM client, embeddings, vector store, security.
- **Repository layer** (`app/repositories/*`) — data access (all the SQL queries live here).
- **Model layer** (`app/models/*`) — SQLAlchemy table definitions.

This separation is a strong interview talking point: *"HTTP concerns, business logic, AI logic, and data access are each isolated, so any one can change without breaking the others."*

---

## 4. Complete file-by-file map

### 4.1 Root

| File | Contains |
|------|----------|
| `pyproject.toml` | Python project metadata + **all backend dependencies** (no `requirements.txt`). Install with `pip install -e .`. |
| `.env` / `.env.example` | Environment config (Gemini API key, thresholds, TLS options). `.env` is git-ignored (secrets). |
| `README.md` | Minimal. **This document** is the real documentation. |
| `data/` | Runtime data: `helpdesk.db` (SQLite), `chroma/` (vector DB), `uploads/` (attachments). |

### 4.2 Backend — `backend/`

**Top-level scripts**

| File | Purpose |
|------|---------|
| `seed.py` | Creates demo users, roles, KB articles, and 3 demo tickets. Run once: `python backend/seed.py`. |
| `kb_articles.py` | The **knowledge base source** — 30 structured articles (Title/Category/Issue/Solution). This *is* the "documents" for RAG. |
| `reindex.py` | Rebuilds the entire vector store from SQLite. Run after changing the embedding model. |
| `check_db.py` | Small script to inspect the DB. |
| `run_dev.py` | Convenience launcher for the dev server. |

**`app/main.py`** — FastAPI entry point. Creates the app, adds CORS, wires up all routers, defines `/health` and `/status`, and on startup: initializes the DB + "pre-warms" the LLM/embedding backends in a background thread (so the first real request isn't slow).

**`app/core/` — infrastructure**

| File | Contains |
|------|----------|
| `config.py` | `Settings` (pydantic-settings). All tunables: DB URL, ChromaDB dir, **confidence threshold (0.70)**, KB-match min score (0.68), duplicate thresholds (0.90 merge / 0.85 suggest), Gemini model names, TLS options. Loaded once and cached. |
| `database.py` | SQLAlchemy engine + `SessionLocal` + `get_db()` dependency + `init_db()` (creates tables). |
| `security.py` | Password hashing (bcrypt), opaque session tokens (in-memory — **no JWT/OAuth2**), and the **`Role`** constants (employee, it_agent, admin_agent, helpdesk_manager, kb_admin, system_admin). |
| `gemini.py` | Builds the shared Gemini client (with TLS policy). Cached via `@lru_cache`. Returns `None` if no API key. |
| `llm.py` | `llm_complete(prompt, system)` → calls Gemini for text generation. Has **timeouts + retries**, and **never raises** — returns `available=False` so callers degrade gracefully. |
| `embeddings.py` | `embed(text, task_type)` → turns text into a vector. Chooses a backend once: **Gemini → sentence-transformers → hashing fallback**. Key detail below. |
| `vectorstore.py` | Wraps ChromaDB (with a NumPy-cosine fallback). All KB/ticket vector operations. Key detail below. |
| `tls.py` | Applies outbound TLS policy (for corporate proxies). Not important for the AI logic. |
| `diagnostics.py` | Startup health check of the AI stack (backend, vector count, smoke retrieval). Powers `/admin/diagnostics`. |

**`app/agents/` — the AI pipeline**

| File | Agent | Job |
|------|-------|-----|
| `base.py` | — | `AgentResult` dataclass (uniform output) + `extract_json()` helper for parsing LLM replies. |
| `ocr_agent.py` | **OCRAgent** | Extract text from a screenshot via pytesseract; no-op stub if unavailable. |
| `intent_agent.py` | **IntentAgent** | Classify category + intent. LLM-based, with a **keyword rule-based fallback**. |
| `priority_agent.py` | **PriorityAgent** | Score urgency (rule-based, explainable) → low/medium/high/critical. |
| `duplicate_agent.py` | **DuplicateAgent** | Vector-similarity vs open tickets. Two tiers: merge (≥0.90) / suggest (≥0.85). |
| `rag_agent.py` | **RAGAgent** | Retrieve KB chunks + ask Gemini for a grounded answer + confidence. |
| `routing_agent.py` | **RoutingAgent** | Map category → department queue. |
| `audit_agent.py` | **AuditAgent** | Persist every agent decision to the `audit_logs` table. |
| `orchestrator.py` | **AgentOrchestrator** | Runs all the above in order and makes the final resolve/route decision. **The heart of the app.** |

**`app/services/` — business logic**

| File | Contains |
|------|----------|
| `ticket_service.py` | Ticket submission (with **idempotency**), lifecycle (escalate/resolve/close), feedback→re-escalation, access control. Calls the orchestrator. |
| `kb_service.py` | KB article CRUD + **chunking** (`_chunk`) + re-indexing into ChromaDB + semantic search. |
| `analytics_service.py` | Computes KPIs: auto-resolution rate, routing accuracy, avg resolution/first-response time, escalation rate, CSAT. |
| `auth_service.py` | Register / login. |
| `notification_service.py` | Creates in-app notifications on ticket events. |

**`app/repositories/` — data access** — one class per entity (`ticket_repo`, `user_repo`, `article_repo`, `feedback_repo`, `log_repo`, `notification_repo`). All the `SELECT/INSERT` logic. The `user_repo` also has `pick_available_agent(department)` for auto-assignment.

**`app/models/` — SQLAlchemy tables** — `user.py`, `ticket.py`, `feedback.py`, `log.py` (audit), `notification.py`, `role.py`. Also defines the `TicketStatus` and `Department` constant classes.

**`app/api/` — HTTP routers** — `auth.py`, `tickets.py`, `knowledge.py`, `analytics.py`, `notifications.py`, `admin.py`, plus `deps.py` (resolves the acting user from the `X-User-Email` header).

**`app/schemas.py`** — all Pydantic request/response shapes.

### 4.3 Frontend — `frontend/src/`

| Path | Contains |
|------|----------|
| `main.jsx` | App bootstrap: wraps everything in QueryClientProvider (react-query), ThemeProvider (MUI), UserProvider, BrowserRouter. |
| `App.jsx` | Route table + role-based guards (`RequireUser`, `RequireKbAccess`, `RequireManualTeam`). |
| `config.js` | `API_BASE_URL` (from `VITE_API_URL` env, defaults to `http://localhost:8000`). |
| `context/UserContext.jsx` | Holds the logged-in user in React context + role helpers + `homePathForRole()`. |
| `api/client.js` | The single axios instance. Interceptor attaches `X-User-Email` to every request. |
| `api/*.js` | One module per domain (`tickets.js`, `auth.js`, `knowledge.js`, `analytics.js`, `notifications.js`, …) — thin wrappers over axios. |
| `hooks/*.js` | react-query hooks (`useTickets`, `useKnowledge`, `useAnalytics`, …) — the components' data source. |
| `pages/*.jsx` | One page per persona: `LoginPage`, `EmployeePage`, `AgentPage`, `ManagerPage`, `KnowledgeBasePage`, `EscalationsPage`, `DatabasePage`. |
| `components/*.jsx` | Reusable UI: `TicketForm`, `TicketList`, `TicketDetail`, `Dashboard`, `DuplicateSuggestions`, `FeedbackForm`, `Layout`, `Navbar`, `Sidebar`, `NotificationBell`, `StatusChip`, `ArticleList`, `ArticleView`. |

---

## 5. The RAG pipeline in detail (the part you most need to explain)

This section answers: *how is content extracted, chunked, embedded, stored, searched, given to the LLM, scored, and summarized?*

### Step 0 — Where "documents" come from

There is **no file upload / parsing** for the knowledge base. The source is `backend/kb_articles.py`: a Python list of 30 dicts, each like:

```python
{
  "title": "Password Reset",
  "category": "Password/Access",
  "issue": "User forgot account password.",
  "solution": "Navigate to the password reset portal. Verify identity using MFA. ...",
}
```

`seed.py` calls `format_article_content(issue, solution)` → builds a body string:

```
Issue: User forgot account password.

Solution: Navigate to the password reset portal. ...
```

…and saves it as a `KnowledgeArticle` row in **SQLite**, then indexes it (next steps).

### Step 1 — Chunking (`kb_service._chunk`)

Location: `backend/app/services/kb_service.py`.

- Before chunking, the **title is prepended to the body** (`f"{title}\n\n{content}"`) so a query matching the title also retrieves the article.
- Chunking is **sentence-aware**: it splits on sentence boundaries (`. ! ?`) and packs whole sentences into chunks of **≤ 1000 characters**, never cutting mid-sentence.
- Most helpdesk articles are short, so they become **a single chunk**. Each chunk gets an id `art-{article_id}-{i}` and metadata `{article_id, title, category}`.

```python
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
def _chunk(text, max_len=1000):
    # normalize whitespace, then greedily pack whole sentences up to max_len
```

### Step 2 — Embedding (`app/core/embeddings.py`)

Each chunk is turned into a vector by `embed(text, task_type)`.

- **Backend is resolved once** and cached (so every vector shares the same dimension). Priority:
  1. **Gemini** `gemini-embedding-001` (3072-dim) — the real semantic embedder. Probed with retries at startup.
  2. **sentence-transformers** `all-MiniLM-L6-v2` (local, if installed).
  3. **Hashing fallback** (384-dim, deterministic) — last resort, *not* semantic. When this is active, duplicate detection is disabled (see `is_semantic_backend()`) to avoid false matches.
- **Task types matter** for Gemini quality:
  - KB chunks → `RETRIEVAL_DOCUMENT`
  - RAG search query → `RETRIEVAL_QUERY`
  - ticket-vs-ticket duplicate check → `SEMANTIC_SIMILARITY`
- Vectors are **L2-normalized**, so a dot product equals cosine similarity (fast + simple).
- Robustness: Gemini calls run in a thread pool with a **30s timeout and 3 retries**; a persistent failure returns a dimension-safe **zero vector** (which is cosine-0 with everything → no false matches) rather than corrupting the index.

### Step 3 — Storing vectors (`app/core/vectorstore.py`)

Two ChromaDB **collections**:

- `kb_chunks` — knowledge base chunk vectors (for RAG).
- `ticket_embeddings` — open-ticket vectors (for duplicate detection).

`add_kb_chunks(items)` embeds all chunks and **upserts** them into `kb_chunks`. There's a transparent fallback: if ChromaDB can't load, a **`_NumpyStore`** persists vectors to JSON and does cosine search with NumPy — identical behavior, so RAG works anywhere.

### Step 4 — Similarity search / retrieval (`search_kb`)

When a ticket arrives, `search_kb(query, top_k=4)`:

1. Embeds the query with `RETRIEVAL_QUERY`.
2. Asks the vector store for the `top_k` nearest chunks.
3. ChromaDB returns a **distance**; the code converts it to a **cosine-like similarity score in [0,1]**: `score = max(0, 1 - distance/2)`.
4. Returns each hit as `{id, document, metadata, score}`.

This is the **"similarity check"**: query vector vs every stored chunk vector, ranked by closeness.

### Step 5 — Generation (the "G" in RAG) — `app/agents/rag_agent.py`

`RAGAgent.run(query)`:

1. Retrieves the top chunks (Step 4). Records `retrieval_strength = max(chunk scores)`.
2. If **no chunks** → returns empty answer, confidence 0 (→ route to a human).
3. Builds a **context block** from the retrieved chunks:
   ```
   [1] Password Reset
   Issue: ... Solution: ...

   [2] VPN Connection Failure
   ...
   ```
4. Builds a prompt telling Gemini to **answer ONLY from the context** and reply in **JSON**:
   ```
   Return JSON: {"answer": <grounded answer citing [n]>, "confidence": <0..1>}
   ```
   with a system instruction: *"Answer ONLY from the provided knowledge base context. If insufficient, say so and set low confidence."* — this is the **anti-hallucination guard**.
5. Calls `llm_complete()`. If the LLM is unavailable → confidence 0 (graceful degradation).
6. Parses the JSON, then computes a **blended confidence**:
   ```
   confidence = 0.6 * llm_self_confidence + 0.4 * retrieval_strength
   ```
   This is the **scoring**: it combines how confident the model says it is with how strong the vector match was. (The "summarization" is exactly this grounded `answer` field the LLM produces.)

Returns `{answer, sources, retrieval_strength}` + `confidence`.

### Step 6 — The decision (`orchestrator.process`, step 6)

The orchestrator applies four rules using two thresholds from config:

- `retrieval_strength ≥ kb_match_min_score (0.68)` → "we have a real KB match"
- `confidence ≥ ai_confidence_threshold (0.70)` → "the AI is confident enough"

| Condition | Outcome |
|-----------|---------|
| KB match **and** confidence ≥ 0.70 **and** answer exists | ✅ **Auto-resolve** — status `resolved`, `resolution_source = "auto"`, store citations. |
| KB match but confidence < 0.70 | ⚠️ **Escalate to L2** (ambiguous). |
| No KB match but a recognized category | ⚠️ **Escalate to L2**. |
| No KB match and category = "Other" | ⏳ Leave **in_progress** (awaiting classification/KB entry). |

Escalation routes to the correct department (RoutingAgent) and auto-assigns an available agent.

---

## 6. The multi-agent orchestrator — full walkthrough

File: `backend/app/agents/orchestrator.py`. Method: `process(ticket)`. Called by `TicketService.submit()`.

```
Input text = ticket.title + ticket.description   (+ OCR text if a screenshot)

Step 1  OCR        → ocr_text                       [OCRAgent]
Step 2  Intent     → category, intent, conf         [IntentAgent]   (LLM or keyword fallback)
Step 3  Priority   → priority band + score          [PriorityAgent] (rule-based)
Step 4  Duplicate  → is_duplicate?, suggestions     [DuplicateAgent](vector similarity)
          ├─ if duplicate of a RESOLVED ticket → reuse its resolution → RESOLVED (source=duplicate_match)
          └─ if duplicate of an UNRESOLVED ticket → status=DUPLICATE, linked
Step 5  RAG        → answer, sources, confidence     [RAGAgent]      (retrieval + Gemini)
Step 6  Decision   → auto-resolve / escalate-L2 / in_progress   (thresholds)

Every step is recorded by the AuditAgent into audit_logs.
The ticket's own vector is upserted into `ticket_embeddings` so future tickets
can detect it as a duplicate.
Returns: (pipeline_steps_trace, duplicate_suggestions)
```

Two agents were **deliberately removed** (documented in the file header): a Vision agent and a separate Embedding agent — their outputs were recorded but never influenced the outcome, so they were dead weight. (Good thing to mention: shows you understand *why* code exists, not just *what*.)

### Each agent, one line:

- **OCRAgent** — `pytesseract` OCR on the attachment; graceful stub if Tesseract isn't installed.
- **IntentAgent** — asks Gemini to pick one of 9 categories + an intent + confidence. If Gemini is down, a **keyword classifier** (dictionaries of cue words per category) takes over. Never fails.
- **PriorityAgent** — pure rules: urgency cue words ("urgent", "down", "outage"…) + category weighting → score → band. Deterministic and explainable on purpose.
- **DuplicateAgent** — embeds the ticket, searches `ticket_embeddings`. ≥0.90 = auto-merge; 0.85–0.90 = "possibly related" suggestion; <0.85 = ignored. **Disabled entirely** if only the non-semantic hashing embedder is active (prevents false positives).
- **RAGAgent** — described in Section 5.
- **RoutingAgent** — static map: Password/Hardware/Software/Network/Email → IT; HR/Payroll → HR; Finance → Finance; Facilities → Facilities; Other → General.
- **AuditAgent** — writes structured records (agent name, model version, confidence, input/output) to `audit_logs`.

---

## 7. FastAPI endpoints — the complete API surface

Base URL: `http://localhost:8000`. The API is **public** (no auth token). The acting user is inferred from an optional `X-User-Email` header (see `app/api/deps.py`); if absent it defaults to `employee@demo.com`. RBAC role checks exist in code but are **non-enforcing** in this MVP.

### Auth — `app/api/auth.py`

| Method | Path | Calls | Purpose |
|--------|------|-------|---------|
| GET | `/auth/users` | direct query | List users (persona picker for "lite login"). |
| POST | `/auth/register` | `AuthService.register` | Create a user. |
| POST | `/auth/login` | `AuthService.login` | Log in → token + role. |
| GET | `/auth/me` | `get_current_user` | Current acting user. |

### Tickets — `app/api/tickets.py` (the main flow)

| Method | Path | Calls | Purpose |
|--------|------|-------|---------|
| POST | `/tickets` | `TicketService.submit` → **AgentOrchestrator.process** | Submit a ticket (multipart: description, title, optional attachment). Runs the whole AI pipeline. Returns ticket + pipeline trace + duplicate suggestions. |
| GET | `/tickets` | `TicketService.list_for_user` | List tickets scoped to the persona (employee sees own; agent sees dept + assigned; manager sees all). |
| GET | `/tickets/escalations` | `TicketService.list_escalations` | Manual-team dashboard (escalated tickets + employee contact + feedback). |
| GET | `/tickets/{id}` | `TicketService.get_for_user` | One ticket (with access check). |
| GET | `/tickets/{id}/audit` | `TicketService.audit_trail` | Full audit log for a ticket. |
| POST | `/tickets/{id}/escalate` | `TicketService.escalate` | Escalate to L2/L3/vendor. |
| POST | `/tickets/{id}/resolve` | `TicketService.resolve` | Agent/manager manual resolution. |
| POST | `/tickets/{id}/close` | `TicketService.close` | Close a ticket. |
| POST | `/tickets/{id}/feedback` | `TicketService.add_feedback` | 👍/👎 feedback. A 👎 on an AI resolution **auto-re-escalates** to a human. |

### Knowledge base — `app/api/knowledge.py`

| Method | Path | Calls | Purpose |
|--------|------|-------|---------|
| GET | `/kb/articles` | `KBService.list` | List all articles. |
| GET | `/kb/search?q=` | `KBService.search` | **Semantic search** over the vector store. |
| GET | `/kb/articles/{id}` | `KBService.get` | One article. |
| POST | `/kb/articles` | `KBService.create` | Create (re-embeds). KB-admin only. |
| PUT | `/kb/articles/{id}` | `KBService.update` | Update (re-embeds). KB-admin only. |
| DELETE | `/kb/articles/{id}` | `KBService.delete` | Delete (removes vectors). KB-admin only. |

### Analytics / Notifications / Admin / System

| Method | Path | Calls | Purpose |
|--------|------|-------|---------|
| GET | `/analytics` | `AnalyticsService.compute` | KPIs (manager/admin). |
| GET | `/notifications` | `NotificationRepository` | Per-persona notifications (frontend polls every 30s). |
| POST | `/notifications/{id}/read` | `NotificationRepository.mark_read` | Mark read. |
| GET | `/admin/db` | direct queries | Row counts + recent records (Database page). |
| GET | `/admin/diagnostics` | `run_diagnostics` | AI-stack health. |
| GET | `/health` | — | Liveness. |
| GET | `/status` | — | LLM configured?, vector backend, KB chunk count, thresholds. |

**Swagger UI** is auto-generated at `http://localhost:8000/docs` — a great thing to open live during the interview.

---

## 8. The data model (SQLite tables)

| Table | Model file | Key columns |
|-------|-----------|-------------|
| `users` | `models/user.py` | id, email, full_name, hashed_password, **role_name**, department, is_available. |
| `tickets` | `models/ticket.py` | id, employee_id, title, description, ocr_text, **intent, category, priority, priority_score, confidence**, status, resolution, **resolution_source** (auto/agent/duplicate_match), kb_sources (JSON citations), department, assigned_agent_id, duplicate_of_id, escalation_target, routing_reason, **idempotency_key**, timestamps. |
| `knowledge_articles` | `models/ticket.py` | id, title, content, category, **retrieval_count**, author_id, timestamps. |
| `feedback` | `models/feedback.py` | id, ticket_id, user_id, rating (0/1), comment. |
| `audit_logs` | `models/log.py` | event, ticket_id, actor, agent_name, model_version, confidence, input/output JSON, created_at. |
| `notifications` | `models/notification.py` | type, message, ticket_id, is_read, recipient_role. |
| `roles` | `models/role.py` | name, description. |

**Ticket lifecycle states:** `open → in_progress / routed / escalated / resolved / closed / duplicate`.

**Vector data (not SQL, in ChromaDB):** `kb_chunks` collection + `ticket_embeddings` collection under `data/chroma/`.

---

## 9. Frontend architecture & data flow

1. **`main.jsx`** wraps the app in providers: react-query (server cache), MUI theme, `UserProvider` (who's logged in), `BrowserRouter`.
2. **`App.jsx`** defines routes and **role guards**. A user in context is required (`RequireUser`), and some pages are restricted (KB page hidden from plain employees; Escalations page limited to agents/managers). `homePathForRole()` sends each persona to their landing page.
3. **`UserContext`** stores the selected user in React state + `sessionStorage` (so a refresh keeps you logged in). There's no real auth session — the "login" just picks a persona.
4. **`api/client.js`** — one axios instance; an interceptor stamps every request with the `X-User-Email` header (this is how the backend knows the persona).
5. **`hooks/*`** — react-query hooks are the components' data source. Example (`useTickets.js`):
   - `useTickets()` → GET `/tickets` (cached under key `['tickets']`).
   - `useSubmitTicket()` → POST `/tickets`, then **invalidates** the `['tickets']` cache so the list refetches automatically.
   - Lifecycle mutations (`useResolveTicket`, `useEscalateTicket`, `useCloseTicket`, `useSubmitFeedback`) invalidate the relevant caches on success.
6. **Pages/components** render the data. E.g. `EmployeePage` shows `TicketForm` (submit) + `TicketList` → `TicketDetail` (which shows the AI resolution, KB citations, duplicate suggestions, and a `FeedbackForm`).

**Frontend data flow example (submitting a ticket):**

```
TicketForm  →  useSubmitTicket()  →  submitTicket()  →  axios POST /tickets (multipart)
     ▲                                                          │
     │                                                          ▼
 react-query invalidates ['tickets']  ◄───────────────  FastAPI runs the pipeline,
 → TicketList refetches & shows the                     returns {ticket, pipeline, suggestions}
   new ticket with its AI outcome
```

---

## 10. End-to-end example: "I forgot my password and I'm locked out"

1. **Frontend**: employee types the ticket in `TicketForm`, hits submit. `useSubmitTicket` → `POST /tickets` (multipart) with `X-User-Email: employee@demo.com`.
2. **API** (`tickets.submit_ticket`): saves any attachment, calls `TicketService.submit(...)`.
3. **Service**: checks idempotency, creates the `Ticket` row (status `open`), logs `ticket_submitted`, calls `AgentOrchestrator.process(ticket)`.
4. **Orchestrator**:
   - OCR: no attachment → skip.
   - Intent: Gemini → `category = "Password/Access"`, intent `reset_password`, confidence ~0.9.
   - Priority: cue "locked" → `medium/high`.
   - Duplicate: embeds the text, searches `ticket_embeddings` → no ≥0.90 match → continue.
   - RAG: embeds query → retrieves the **"Password Reset"** KB chunk (score ~0.75) → Gemini writes a grounded, step-by-step answer citing `[1]`, self-confidence ~0.9 → blended confidence ≈ `0.6*0.9 + 0.4*0.75 = 0.84`.
   - Decision: KB match (0.75 ≥ 0.68) **and** confidence (0.84 ≥ 0.70) → **auto-resolve**. Status `resolved`, `resolution_source = "auto"`, citations saved.
   - Upserts the ticket's final vector; every step logged.
5. **Service**: status is `resolved` → notifies the employee.
6. **API**: returns `{ticket, pipeline[...], duplicate_suggestions[]}`.
7. **Frontend**: react-query invalidates the list; `TicketDetail` shows the AI answer, the KB citation, and the pipeline trace. The employee can 👍/👎. A 👎 re-escalates to a human.

---

## 11. Design decisions worth defending in the interview

- **Why SQLite + ChromaDB (not one DB)?** Relational data (users, tickets, relationships, transactions) fits a **relational DB**; embeddings need **nearest-neighbor search**, which is what a **vector DB** is built for. Two stores, each doing what it's best at.
- **Why no LangChain?** The pipeline is small and specific; hand-writing it keeps dependencies light, behavior transparent, and debugging simple. (Trade-off: more code, but full control.)
- **Graceful degradation everywhere.** No Gemini key? → keyword classifier + route to humans. Gemini times out? → retries, then degrade this one call. ChromaDB wheel missing? → NumPy fallback. Non-semantic embedder? → disable duplicate detection. **The app never crashes because an AI component is unavailable.** This is the strongest theme in the codebase.
- **Confidence blending** (`0.6*LLM + 0.4*retrieval`) avoids trusting the LLM's self-assessment alone, and avoids auto-resolving on a weak retrieval.
- **Idempotency** on submission prevents double-running the (expensive) AI pipeline on a retried request.
- **Full audit trail** (every agent decision logged with model version + confidence) = AI governance / explainability.
- **Task-typed embeddings** (`RETRIEVAL_DOCUMENT` vs `RETRIEVAL_QUERY` vs `SEMANTIC_SIMILARITY`) measurably improve retrieval and duplicate accuracy.

---

## 12. How to run it

**Backend:**
```bash
pip install -e .                 # install deps from pyproject.toml
# set GEMINI_API_KEY in .env
python backend/seed.py           # create demo users + KB + tickets
python backend/reindex.py        # (optional) rebuild vectors
uvicorn app.main:app --reload --app-dir backend    # or: python backend/run_dev.py
# API at http://localhost:8000 , Swagger at /docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                      # Vite dev server (usually http://localhost:5173)
```

**Demo users** (password `Password123` for all): `employee@demo.com`, `it.agent@demo.com`, `hr.agent@demo.com`, `finance.agent@demo.com`, `manager@demo.com`, `kbadmin@demo.com`, `sysadmin@demo.com`.

---

## 13. 60-second summary (memorize this)

> "It's a full-stack AI helpdesk router. Employees submit tickets to a **FastAPI** backend. A **multi-agent orchestrator** runs the ticket through OCR, LLM-based intent classification, rule-based priority, vector-based duplicate detection, and a **RAG** step. RAG works like this: our knowledge base articles are **chunked**, **embedded** with **Gemini** into vectors, and stored in **ChromaDB**. When a ticket comes in, we embed the ticket text, do a **cosine-similarity search** to pull the most relevant chunks, feed them to **Gemini** as grounding context, and get back a **grounded answer plus a confidence score**. If confidence and retrieval strength are both high, the ticket is **auto-resolved**; otherwise it's **routed** to the right human department. Everything is **logged** for governance, and **every AI component degrades gracefully** if it's unavailable. Structured data is in **SQLite** via SQLAlchemy; the frontend is **React** with **react-query**. No MongoDB, no LangChain — the RAG pipeline is hand-built."
