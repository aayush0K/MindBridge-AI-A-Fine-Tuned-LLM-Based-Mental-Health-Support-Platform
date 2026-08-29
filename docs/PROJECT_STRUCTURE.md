# Project Structure

A complete map of every file in the repository and its purpose.

---

```
mindbridge-ai/
│
├── README.md                    ← Project overview and quick start
├── CHANGELOG.md                 ← Version history (Keep a Changelog)
├── CONTRIBUTING.md              ← Developer guide and PR process
├── CODE_OF_CONDUCT.md           ← Community standards
├── SECURITY.md                  ← Vulnerability reporting and security design
├── ROADMAP.md                   ← Planned features by version
├── LICENSE                      ← MIT License
├── docker-compose.yml           ← PostgreSQL 16 + Redis 7 services
│
├── docs/
│   ├── ARCHITECTURE.md          ← System design, AI pipeline, DB schema
│   ├── API.md                   ← Full REST + WebSocket API reference
│   ├── DEPLOYMENT.md            ← Production deployment guide
│   ├── FAQ.md                   ← Common setup and usage questions
│   ├── PROJECT_STRUCTURE.md     ← This file
│   └── LOCAL_SETUP.md           ← Quick environment variable reference
│
├── backend/
│   ├── .env.example             ← Template for required environment variables
│   ├── alembic.ini              ← Alembic database migration configuration
│   ├── requirements.txt         ← Python production + test dependencies
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              ← FastAPI app, lifespan, CORS, route registration
│   │   ├── config.py            ← Pydantic Settings (reads .env)
│   │   ├── database.py          ← Async SQLAlchemy engine + session factory
│   │   ├── dependencies.py      ← FastAPI DI: JWT auth → current user
│   │   │
│   │   ├── api/v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py        ← APIRouter aggregating all v1 subrouters
│   │   │   ├── auth.py          ← /auth/* endpoints (register, login, refresh, logout)
│   │   │   ├── chat.py          ← /chat/* endpoints (message, sessions, delete)
│   │   │   ├── mood.py          ← /mood/* endpoints (log, history, stats)
│   │   │   └── users.py         ← /users/me endpoint
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py      ← Imports all models (required for Alembic autodiscovery)
│   │   │   ├── user.py          ← User SQLAlchemy model
│   │   │   ├── session.py       ← ChatSession SQLAlchemy model
│   │   │   ├── message.py       ← Message SQLAlchemy model
│   │   │   ├── mood_log.py      ← MoodLog SQLAlchemy model
│   │   │   ├── classifier_weights.pt  ← Trained PyTorch classifier (103KB, versioned)
│   │   │   └── label_map.json   ← Category index ↔ name mapping (required at inference)
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          ← Register/Login/Token request+response schemas
│   │   │   ├── chat.py          ← SendMessageRequest, ChatResponse, SessionResponse, etc.
│   │   │   ├── mood.py          ← MoodLogRequest, MoodLogResponse, MoodStatsResponse
│   │   │   └── user.py          ← UserResponse schema
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py    ← Main AI pipeline orchestrator (Steps 1–9)
│   │   │   ├── embedder.py      ← MentalHealthEmbedder (MiniLM, corpus, few-shot)
│   │   │   ├── classifier.py    ← MentalHealthClassifier PyTorch model definition
│   │   │   ├── classifier_service.py  ← Model loading + MC Dropout inference wrapper
│   │   │   ├── crisis_service.py      ← Keyword crisis detection (regex, CRISIS_RESPONSE)
│   │   │   ├── memory_service.py      ← Redis conversation memory (MemoryService)
│   │   │   └── auth_service.py        ← JWT + bcrypt helper functions
│   │   │
│   │   └── ws/
│   │       ├── __init__.py
│   │       └── chat_ws.py       ← WebSocket /ws/chat handler
│   │
│   ├── corpus/
│   │   └── mental_health_corpus.json  ← 1,247-entry mental health Q&A corpus (127KB)
│   │                                    Used for embedding retrieval + classifier training
│   │
│   ├── migrations/
│   │   ├── env.py               ← Alembic environment (reads app models)
│   │   ├── script.py.mako       ← Migration file template
│   │   └── versions/            ← Versioned migration scripts
│   │
│   ├── scripts/
│   │   ├── train_classifier.py  ← Train MentalHealthClassifier on corpus (run to regenerate weights)
│   │   └── generate_corpus.py   ← Script used to build mental_health_corpus.json
│   │
│   └── tests/
│       ├── test_ai_pipeline.py  ← Unit tests: embedder, crisis detection, few-shot (no server)
│       └── e2e_test.py          ← Integration tests: full API flow (requires running server)
│
└── frontend/
    ├── package.json             ← Dependencies (Next.js 14, Zustand, Recharts, etc.)
    ├── tsconfig.json            ← TypeScript configuration
    ├── tailwind.config.ts       ← Tailwind CSS theme
    ├── next.config.js           ← Next.js configuration
    ├── .env.local.example       ← Frontend environment variable template
    │
    ├── app/                     ← Next.js 14 App Router
    │   ├── layout.tsx           ← Root layout (fonts, global CSS)
    │   ├── globals.css          ← Global Tailwind + custom styles
    │   ├── page.tsx             ← Landing / redirect page
    │   ├── login/               ← Login page
    │   ├── register/            ← Registration page
    │   └── dashboard/           ← Main app: chat + mood tracking
    │
    ├── components/
    │   ├── chat/                ← ChatWindow, MessageBubble, MessageInput
    │   ├── dashboard/           ← DashboardLayout, SessionList, MoodChart
    │   ├── layout/              ← Sidebar, TopNav
    │   └── ui/                  ← Shared primitives (Button, Input, Dialog, etc.)
    │
    ├── lib/
    │   ├── api.ts               ← Axios API client (auth headers, base URL)
    │   └── utils.ts             ← Tailwind class merge utility (cn())
    │
    ├── store/
    │   └── chatStore.ts         ← Zustand global state (sessions, messages, auth)
    │
    └── types/
        ├── chat.types.ts        ← TypeScript types for chat data
        └── user.types.ts        ← TypeScript types for user/auth data
```

---

## Key Files at a Glance

| File | Why It Matters |
|---|---|
| `backend/app/services/ai_service.py` | The heart of the system — runs the 9-step AI pipeline on every message |
| `backend/app/services/crisis_service.py` | Safety-critical — the keyword crisis detector. Handle with care |
| `backend/app/services/memory_service.py` | Redis conversation memory — atomic writes, TTL, graceful degradation |
| `backend/app/services/classifier_service.py` | ML classifier loader + MC Dropout inference |
| `backend/app/services/embedder.py` | MiniLM embedder + cosine similarity + corpus operations |
| `backend/app/models/classifier_weights.pt` | Trained PyTorch weights — do not delete; regenerate with `scripts/train_classifier.py` |
| `backend/corpus/mental_health_corpus.json` | The knowledge base for retrieval and training — central to AI quality |
| `docker-compose.yml` | Single command to start the entire infrastructure |
| `backend/.env.example` | The authoritative list of all configuration knobs |

---

## Files Intentionally Absent

| Absent File | Reason |
|---|---|
| `backend/.env` | Contains secrets — gitignored; use `.env.example` as template |
| `frontend/.env.local` | Contains environment-specific URLs — gitignored |
| `backend/venv/` | Python virtual environment — gitignored; recreate with `pip install -r requirements.txt` |
| `frontend/node_modules/` | Node.js packages — gitignored; recreate with `npm install` |
| `**/__pycache__/` | Python bytecode cache — gitignored |
