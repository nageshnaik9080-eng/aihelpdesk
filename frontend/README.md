# AI Helpdesk Router — Frontend

React + JavaScript + Vite + Material-UI (MUI) client for the AI-Powered IT/Admin
Helpdesk Router. Talks to the FastAPI backend over Axios; server state is managed
with TanStack **React Query**; navigation with **React Router**.

Backend calls go over plain **HTTP** (`http://localhost:8000`) — there is no TLS,
so no SSL certificate for the browser to verify.

## Auth model (important)

The backend API is **public** — no JWT, no OAuth2, no Swagger "Authorize" button.
The frontend uses a lightweight login only to establish *identity + role* (via
`POST /auth/login`). The chosen user is stored locally and sent on every request
as an `X-User-Email` header (see `src/api/client.js`), which the backend resolves
to scope persona-specific data. If the header is missing the backend falls back to
a default demo user.

## Prerequisites

- Node 18+ (developed on Node 24)
- The backend running at `http://localhost:8000` (see below)

## Run

```bash
# 1) Backend (from the repo root)
cd backend
uvicorn app.main:app --reload
#    First time only — seed demo users, KB articles & tickets:
#    python ../backend/seed.py   (or: python backend/seed.py from repo root)

# 2) Frontend (from the repo root)
cd frontend
npm install
npm start          # or: npm run dev  → http://localhost:5173
```

Sign in with a seeded demo user (password `Password123`), e.g.:

| Email | Role | View |
|-------|------|------|
| employee@demo.com | employee | Submit & track tickets |
| it.agent@demo.com | it_agent | Agent queue (resolve / escalate) |
| manager@demo.com | helpdesk_manager | Analytics dashboard |
| kbadmin@demo.com | kb_admin | Knowledge base (+ create articles) |

## Configuration

`VITE_API_URL` (in `.env`) points at the backend. Defaults to
`http://localhost:8000`.

## Scripts

| Script | Purpose |
|--------|---------|
| `npm start` / `npm run dev` | Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview the production build |
| `npm test` | Run Jest + React Testing Library |

## Structure

```
src/
  api/          Axios client + endpoint wrappers
  hooks/        React Query hooks (tickets, knowledge, analytics)
  context/      UserContext (current persona) + role helpers
  components/   Reusable UI: Navbar, Sidebar, Layout, TicketForm, TicketList,
                DuplicateSuggestions, FeedbackForm, ArticleList, ArticleView,
                TicketDetail, Dashboard, StatusChip
  pages/        LoginPage, EmployeePage, AgentPage, ManagerPage, KnowledgeBasePage
  __tests__/    Jest + RTL component tests
```

## Views ↔ backend endpoints

- **Employee** — `POST /tickets`, `GET /tickets`, `POST /tickets/{id}/feedback`,
  `POST /tickets/{id}/close`; shows duplicate suggestions + AI pipeline trace.
- **Agent** — `GET /tickets`, `POST /tickets/{id}/resolve`,
  `POST /tickets/{id}/escalate`.
- **Manager** — `GET /analytics` (resolution time, routing accuracy, KB usage…).
- **Knowledge base** — `GET /kb/articles`, `GET /kb/search`, `POST /kb/articles`.
