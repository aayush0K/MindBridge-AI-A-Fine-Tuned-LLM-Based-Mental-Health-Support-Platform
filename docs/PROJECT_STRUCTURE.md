# Project Structure

A complete map of every file in the repository and its purpose.

---

```
mindbridge-ai/
│
├── README.md                    ← Project overview, architecture, and quick start
├── CHANGELOG.md                 ← Version history (Keep a Changelog)
├── CONTRIBUTING.md              ← Developer guide and PR process
├── CODE_OF_CONDUCT.md           ← Community standards
├── SECURITY.md                  ← Vulnerability reporting and security design
├── ROADMAP.md                   ← Planned features by version
├── LICENSE                      ← MIT License
├── docker-compose.yml           ← PostgreSQL 16 (pgvector) + Redis 7 services
│
├── docs/
│   ├── ARCHITECTURE.md          ← System design, AI pipeline, DB schema
│   ├── API.md                   ← Full REST + WebSocket API reference
│   ├── DEPLOYMENT.md            ← Production deployment guide
│   ├── FAQ.md                   ← Common setup and architecture questions
│   ├── LOCAL_SETUP.md           ← Quick environment variable & run guide
│   ├── PROJECT_STRUCTURE.md     ← This file
│   ├── remote_gpu_deployment.md ← Google Colab GPU & ngrok inference setup
│   └── semantic_caching.md      ← Semantic response cache deep-dive & benchmarks
│
├── backend/
│   ├── .env.example             ← Template for required environment variables
│   ├── alembic.ini              ← Alembic database migration configuration
│   ├── pytest.ini               ← Pytest configuration with pythonpath=.
│   ├── requirements.txt         ← Python production + test dependencies
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              ← FastAPI app, lifespan, CORS, route registration
│   │   ├── config.py            ← Pydantic Settings (reads .env)
│   │   ├── database.py          ← Async SQLAlchemy 2.0 engine + session factory
│   │   ├── dependencies.py      ← FastAPI DI: JWT auth → current user
│   │   │
│   │   ├── api/v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py        ← APIRouter aggregating all v1 subrouters
│   │   │   ├── auth.py          ← /auth/* endpoints (register, login, refresh, logout)
│   │   │   ├── chat.py          ← /chat/* endpoints (message, sessions, cache-metrics)
│   │   │   ├── mood.py          ← /mood/* endpoints (log, history, stats)
│   │   │   ├── journal.py       ← /journal/* endpoints (create, list, get, delete)
│   │   │   ├── report.py        ← /reports/* endpoints (generate, get)
│   │   │   └── users.py         ← /users/me endpoint
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py      ← Imports and exports all models
│   │   │   ├── user.py          ← User SQLAlchemy model
│   │   │   ├── session.py       ← ChatSession SQLAlchemy model
│   │   │   ├── message.py       ← Message SQLAlchemy model
│   │   │   ├── mood_log.py      ← MoodLog SQLAlchemy model
│   │   │   ├── report.py        ← WellnessReport SQLAlchemy model
│   │   │   ├── journal.py       ← JournalEntry SQLAlchemy model
│   │   │   ├── semantic_cache.py← SemanticCache model with pgvector column
│   │   │   ├── classifier_weights.pt  ← Trained PyTorch classifier weights
│   │   │   └── label_map.json   ← Category index ↔ name mapping
│   │   │
│   │   ├── safety/
│   │   │   ├── __init__.py
│   │   │   ├── input_safety.py  ← Input checks and crisis word boundary filters
│   │   │   ├── output_safety.py ← Clinical claim & foreign emergency number sanitizer
│   │   │   └── pii_filter.py    ← PII detection, reusability validation, mood checks
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          ← Register/Login/Token request+response schemas
│   │   │   ├── chat.py          ← SendMessageRequest, ChatResponse (with cache fields)
│   │   │   ├── mood.py          ← MoodLogRequest, MoodLogResponse, MoodStatsResponse
│   │   │   ├── journal.py       ← JournalRequest, JournalResponse schemas
│   │   │   ├── report.py        ← ReportRequest, ReportResponse schemas
│   │   │   └── user.py          ← UserResponse schema
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py    ← Main AI pipeline orchestrator
│   │   │   ├── cache_service.py ← SemanticCacheService (lookup, store, deduplication)
│   │   │   ├── metrics_service.py ← CacheMetricsTracker (hits, misses, latencies)
│   │   │   ├── embedder.py      ← MentalHealthEmbedder (all-MiniLM-L6-v2, few-shot)
│   │   │   ├── mood_service.py  ← DistilBERT emotion detection pipeline
│   │   │   ├── classifier.py    ← MentalHealthClassifier PyTorch model definition
│   │   │   ├── classifier_service.py  ← Model loading + MC Dropout inference wrapper
│   │   │   ├── crisis_service.py      ← Multi-layer crisis detection (Tele-MANAS)
│   │   │   ├── memory_service.py      ← Redis rolling conversation memory
│   │   │   ├── semantic_memory.py     ← Long-term semantic retrieval
│   │   │   └── auth_service.py        ← JWT + bcrypt helper functions
│   │   │
│   │   └── ws/
│   │       ├── __init__.py
│   │       └── chat_ws.py       ← WebSocket /ws/chat handler
│   │
│   ├── corpus/
│   │   └── mental_health_corpus.json  ← 1,247-entry mental health Q&A corpus
│   │
│   ├── migrations/
│   │   ├── env.py               ← Alembic environment
│   │   └── versions/            ← Versioned migrations (001 to 005_add_semantic_cache)
│   │
│   ├── scripts/
│   │   ├── test_semantic_cache_live.py ← Live end-to-end verification script
│   │   ├── train_classifier.py         ← Train MentalHealthClassifier on corpus
│   │   └── generate_corpus.py          ← Helper to parse corpus datasets
│   │
│   └── tests/
│       ├── conftest.py          ← Shared fixtures
│       ├── test_ai_pipeline.py  ← Unit tests: embedder, crisis detection, few-shot
│       └── test_semantic_cache.py ← 12 automated tests for semantic caching
│
└── frontend/
    ├── package.json             ← Dependencies (Next.js 14, Tailwind, Zustand)
    ├── tsconfig.json            ← TypeScript configuration
    ├── tailwind.config.ts       ← Tailwind CSS theme
    ├── next.config.js           ← Next.js configuration
    ├── .env.local.example       ← Frontend environment variable template
    │
    ├── app/                     ← Next.js 14 App Router
    │   ├── layout.tsx           ← Root layout (fonts, global CSS)
    │   ├── globals.css          ← Global Tailwind + custom styles
    │   ├── page.tsx             ← Landing page
    │   ├── login/               ← Login page
    │   ├── register/            ← Registration page
    │   └── dashboard/           ← Authenticated application pages
    │       ├── layout.tsx       ← Dashboard shell (sidebar, navigation)
    │       ├── page.tsx         ← Overview dashboard (mood chart, quick stats)
    │       ├── chat/            ← Interactive conversational chat interface
    │       ├── mood/            ← Daily mood check-in and trend analytics
    │       ├── journal/         ← Private reflective journal
    │       ├── resources/       ← Crisis lines and self-care resources
    │       └── settings/        ← User profile and preferences
    │
    ├── components/
    │   ├── chat/                ← ChatWindow, MessageBubble, MessageInput
    │   ├── dashboard/           ← StatCard, MoodTrendChart, RecentActivity
    │   ├── layout/              ← Sidebar, TopNav
    │   └── ui/                  ← Reusable design primitives (Button, Input, Card)
    │
    ├── lib/
    │   ├── api.ts               ← Axios API client (auth interceptors, base URL)
    │   └── utils.ts             ← Safe date formatters and class merge utility (cn())
    │
    ├── store/
    │   ├── chatStore.ts         ← Zustand state for chat sessions and active messages
    │   └── authStore.ts         ← Zustand state for authentication tokens
    │
    └── types/
        ├── chat.types.ts        ← TypeScript interfaces for chat & cache metadata
        └── user.types.ts        ← TypeScript interfaces for user/auth data
```

---

## Key Files at a Glance

| File | Why It Matters |
|---|---|
| `backend/app/services/ai_service.py` | The main orchestrator running the 9-step AI pipeline |
| `backend/app/services/cache_service.py` | Semantic cache lookup & storage with cosine distance and mood compatibility |
| `backend/app/services/metrics_service.py` | Tracks real-time cache hits, avoided GPU calls, and latencies |
| `backend/app/safety/output_safety.py` | Strips clinical medical claims and standardizes Indian emergency numbers |
| `backend/app/safety/pii_filter.py` | Strictly blocks personal information from entering the shared semantic cache |
| `backend/app/services/crisis_service.py` | Authoritative safety gate — triggers Tele-MANAS hotline escalation |
| `backend/app/services/memory_service.py` | Redis rolling conversation memory (24h TTL) |
| `docker-compose.yml` | One-command orchestration of PostgreSQL 16 (`pgvector`) and Redis 7 |
| `docs/semantic_caching.md` | Comprehensive architectural and benchmark documentation |
