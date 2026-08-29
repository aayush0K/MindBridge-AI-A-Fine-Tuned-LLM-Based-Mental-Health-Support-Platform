# Changelog

All notable changes to MindBridge AI are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2025-07-09

### Added
- **Full-stack mental health AI platform** — FastAPI backend + Next.js 14 frontend
- **Google Gemini 2.5 Flash integration** — LLM generation with few-shot context injection
- **Three-layer crisis detection pipeline**:
  - Layer 1: Compiled keyword regex with word-boundary matching (100% recall on known phrases)
  - Layer 2: Embedding-based crisis detection (cosine similarity ≥ 0.70 against crisis corpus vectors)
  - Layer 3: MC Dropout classifier with strict confidence thresholds (conf ≥ 0.75, uncertainty < 0.04, min 4 words)
- **Short-message classifier guard**: Messages fewer than 4 words never trust classifier confidence, preventing false positives from "yes", "okay", "I don't know", etc.
- **Redis-backed conversation memory** (MemoryService):
  - Atomic RPUSH+LTRIM+EXPIRE pipelines — no read-modify-write race
  - Rolling 20-message window (10 turns) per session
  - 24-hour TTL, auto-reset on every write
  - Graceful PostgreSQL fallback when Redis is unavailable
- **Trained ML classifier** (`MentalHealthClassifier`):
  - 2-layer feed-forward network (~28K parameters) on frozen `all-MiniLM-L6-v2` embeddings
  - 10 categories: anxiety, depression, stress, sleep, loneliness, self_esteem, grief, anger, relationships, crisis
  - Monte Carlo Dropout (20 passes) for uncertainty estimation
  - Category-aware few-shot retrieval when classifier confidence ≥ 0.55
- **JWT authentication** — access tokens (30 min) + refresh tokens (30 days), bcrypt hashing (rounds=12)
- **Mood tracking API** — log, history, and 30-day statistics with trend detection
- **WebSocket chat endpoint** — real-time messaging alongside REST API
- **PostgreSQL + Alembic** — async SQLAlchemy, versioned schema migrations
- **Enriched chat response payload**: `predicted_category`, `classifier_confidence`, `uncertainty`, `memory_used`, `few_shot_count`, `relevance_score`, `is_crisis`
- **Graceful degradation** at every layer — server never crashes due to missing optional dependencies
- **Docker Compose** — PostgreSQL 16 + Redis 7 (AOF persistence)

### Fixed
- **Crisis false positive**: `is_crisis=false` and `response="CRISIS"` inconsistency eliminated; `final_is_crisis` is now the single source of truth
- **Short-message crisis trigger**: "yes", "okay", "I don't know" no longer trigger crisis protocol
- **Atomic Redis writes**: replaced two-call append with single pipeline for user+assistant turn
- **Gemini model caching**: model object initialized once at startup; not re-instantiated per request
- **Crisis examples in fallback**: Gemini error path no longer returns literal "CRISIS" from corpus examples

### Security
- No secrets committed — `JWT_SECRET_KEY` and `GEMINI_API_KEY` are required env vars with no defaults
- `pydantic-settings` reads `.env` at startup; `.env` is in `.gitignore`
- JWT `type` field checked on every request to prevent access tokens being used as refresh tokens
- Message input capped at 1000 characters before any AI processing
- CORS origins configurable per environment

---

## [0.2.0] — 2025-06 *(Development)*

### Added
- Redis memory integration (v2.1 of memory service)
- Session-scoped conversation history in Gemini prompt
- Crisis classifier threshold hardening
- Pydantic-settings configuration with `.env` loading

### Changed
- Crisis confidence threshold raised from 0.55 → 0.75
- Confidence fallback threshold raised from 0.35 → 0.55
- `MIN_WORDS_FOR_CLASSIFIER_TRUST` set to 4 words

---

## [0.1.0] — 2025-05 *(Development)*

### Added
- Initial FastAPI backend with authentication
- `all-MiniLM-L6-v2` embedding pipeline
- Cosine-similarity few-shot retrieval
- Keyword-based crisis detection
- Next.js 14 frontend with chat interface
- PostgreSQL schema and Alembic migrations

---

[1.0.0]: https://github.com/your-org/mindbridge-ai/releases/tag/v1.0.0
