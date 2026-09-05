# Architecture

This document describes the internal architecture of MindBridge AI in engineering detail.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Next.js 14 Frontend                       │
│  pages: /  · /login · /register · /dashboard · /chat         │
│         /dashboard/mood · /dashboard/journal · /resources    │
│  state:  Zustand (chatStore)                                 │
│  forms:  React Hook Form + Zod                               │
│  charts: Recharts (mood trends)                              │
│  UI:     Tailwind CSS, Radix UI, Lucide icons                │
└─────────────────────────────┬────────────────────────────────┘
                              │  HTTPS / REST / WSS
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ API Layer  (/api/v1/)                                  │  │
│  │   auth.py     → /auth/register /auth/login /auth/...   │  │
│  │   chat.py     → /chat/message /sessions /cache-metrics │  │
│  │   mood.py     → /mood/log /mood/history /mood/stats    │  │
│  │   journal.py  → /journal (create, list, get, delete)   │  │
│  │   report.py   → /reports (generate, get by id)         │  │
│  │   users.py    → /users/me                              │  │
│  │   chat_ws.py  → /ws/chat (WebSocket streaming)        │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Service Layer                                          │  │
│  │   ai_service.py        ← main pipeline orchestrator    │  │
│  │   cache_service.py     ← semantic caching (pgvector)   │  │
│  │   metrics_service.py   ← cache & latency metrics       │  │
│  │   pii_filter.py        ← PII & mood context guard      │  │
│  │   embedder.py          ← MiniLM-L6-v2 embeddings       │  │
│  │   mood_service.py      ← DistilBERT emotion classifier │  │
│  │   crisis_service.py    ← multi-layer crisis detection  │  │
│  │   memory_service.py    ← Redis conversation memory     │  │
│  │   output_safety.py     ← medical & hotline sanitizer   │  │
│  │   auth_service.py      ← JWT + bcrypt                  │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Data Layer                                             │  │
│  │   database.py  ← SQLAlchemy 2.0 asyncpg engine         │  │
│  │   models/      ← User, Session, Message, MoodLog,     │  │
│  │                   WellnessReport, JournalEntry,        │  │
│  │                   SemanticCache                        │  │
│  │   migrations/  ← Alembic versioned schema (001-005)    │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────┬─────────────────────────────┬────────────────┬─────┘
          │                             │                │
          ▼                             ▼                ▼
    PostgreSQL 16                    Redis 7       Remote GPU Server
    (pgvector HNSW store      (24h session memory)  (Meta Llama 3 8B
     & persistent database)                         + MindBridge LoRA)
```

---

## AI Pipeline (Step by Step)

Every call to `POST /api/v1/chat/message` runs the following pipeline inside `ai_service.process_message()`:

### Step 1 — Sanitise
- Strip whitespace, cap at 1000 characters.
- Empty message → return early with an empathetic prompt to say more.

### Step 2 — Embed
- Encode the message using `all-MiniLM-L6-v2` (384-dimensional dense vector).
- Track embedding latency via `CacheMetricsTracker`.
- This single vector is reused for relevance, crisis embedding, classifier, and semantic cache lookup.

### Step 3 — Relevance Gate & Emotion Classification
- Cosine similarity against all corpus embeddings (threshold: **0.25**).
- Automated emotion classification via fine-tuned DistilBERT / trained classifier.
- Off-topic input? The model still responds, gently steering back to wellbeing and emotional state.

### Step 4 — Safety & Crisis Detection (Authoritative Gate)
Three independent safety layers run **first**:

| Layer | Description |
|---|---|
| **Keyword** | `crisis_service.is_crisis_message()` — compiled regex, word-boundary matched. 100% recall on known crisis phrases. |
| **Embedding** | `embedder.check_crisis_embedding()` — cosine similarity to crisis corpus vectors ≥ **0.70**. |
| **Classifier** | Classifier predicted "crisis" AND confidence ≥ **0.78** AND uncertainty < **0.04** AND word count ≥ **5**. |

**Strict Safety Invariant:** If any layer flags a crisis, the system persists the message, immediately returns `CRISIS_RESPONSE` with localized helpline details (Tele-MANAS `14416` / Emergency `112`), and **STOPS**. The semantic cache is **NEVER** consulted, and the Llama GPU is **NEVER** called.

### Step 4.7 — Semantic Cache Lookup (PostgreSQL + pgvector)
- If the query is safe and `SEMANTIC_CACHE_ENABLED=true`:
  - Query active, unexpired rows (`expires_at > now()`) from PostgreSQL `semantic_cache`.
  - Calculate cosine similarity using pgvector (`vector_cosine_ops`).
  - Verify **Mood Context Compatibility**: Ensure a joyful cached response is not returned to an individual experiencing sadness or anger.
- **If Similarity &ge; `SEMANTIC_CACHE_THRESHOLD` (0.90) and Mood Compatible**:
  - ⚡ **CACHE HIT!**
  - Increment `hit_count` and update `last_accessed_at`.
  - Record hit metric and avoid GPU call.
  - Append turn to Redis session memory (ensuring ongoing context continuity).
  - Return cached response immediately (**~20 ms vs ~30 s remote GPU inference**).

### Step 5 — Dynamic Few-Shot Retrieval
- On cache miss, retrieve Top-3 few-shot seed examples matching the user's category.
- Crisis examples are **always excluded** from few-shot generation. Simple greetings bypass retrieval to prevent unnecessary distress framing.

### Step 6 — Build System Prompt & History
- Static system prompt prefix (core empathetic principles, Indian emergency helpline instructions).
- Dynamic few-shot examples from Step 5.
- Load recent conversation turns from Redis (`memory_service.get_history()`), falling back to PostgreSQL message history.
- Append the current user message as the final turn.

### Step 7 — Remote GPU Inference (Meta Llama 3 8B + LoRA)
- HTTP payload sent to `INFERENCE_URL` (Google Colab Tesla T4 or dedicated inference server).
- Generation parameters: `temperature: 0.6`, `max_new_tokens: 300`.
- Measure and record Llama inference latency.

### Step 7.5 — Output Safety Guard
- Run `sanitize_model_output()`:
  - Strips clinical diagnoses and medication prescription language.
  - Replaces foreign emergency numbers (e.g. US 988, 1-800-273-TALK) with Indian national helplines (Tele-MANAS `14416` / `1800-89-14416` and Emergency `112`).

### Step 7.8 — Semantic Cache Storage
- Evaluates candidate via `is_reusable_guidance()`:
  - **PII Filter**: Rejects queries or answers containing names, phone numbers, email addresses, or personal medical specifics.
  - **Length & Error Guard**: Discards error messages or service notices.
  - **Deduplication**: Bypasses insert if a near-identical vector (&gt; 0.98 similarity) is already cached.
- Stores query, embedding, response, mood, category, and 30-day expiration (`expires_at`) into `semantic_cache`.

### Step 8 — Persist Turn
- Append user + assistant turn to Redis rolling memory (`memory_service.append_turn()`).
- Persist messages and auto-detected mood to PostgreSQL audit tables (`messages`, `mood_logs`).
- Update `chat_sessions.message_count` atomically via SQL.

### Step 9 — Return Enriched Payload
Returns `response`, `is_crisis`, `is_relevant`, `relevance_score`, `few_shot_count`, `predicted_category`, `classifier_confidence`, `uncertainty`, `memory_used`, `cache_hit`, and `cached_similarity`.

---

## Memory Engine (Redis)

```
Per session: Redis List — key: "mb:memory:{session_id}"

Write (append_turn):
  RPUSH key user_json
  RPUSH key ai_json
  LTRIM key -20 -1    ← keep newest 20 messages (10 turns)
  EXPIRE key 86400    ← 24h TTL reset on every write
  (executed in a single atomic Redis pipeline)

Read (get_history):
  LRANGE key -12 -1   ← last 12 messages (6 turns for LLM prompt)
```

**Graceful Degradation**: If Redis is temporarily offline, the service automatically falls back to PostgreSQL session history loaded at request start.

---

## Database Schema (PostgreSQL + pgvector)

### `users`
User credentials, hashed password, profile details, and emergency contact email.

### `chat_sessions`
Chat session metadata (`id`, `user_id`, `title`, `message_count`, `crisis_flagged`, `started_at`, `ended_at`).

### `messages`
Audit history of all exchanges (`id`, `session_id`, `role`, `content`, `relevance_score`, `is_crisis`, `detected_mood`, `mood_confidence`, `embedding`, `created_at`).

### `mood_logs`
User mood entries and auto-detected emotional states (`mood_score`, `mood_label`, `confidence`, `auto_detected`).

### `wellness_reports`
Periodic AI-generated emotional summary reports (`period_start`, `period_end`, `summary`, `key_topics`, `mood_analysis`, `recommendations`).

### `journal_entries`
Private user reflective journal entries (`title`, `content`, `mood_tag`, `created_at`, `updated_at`).

### `semantic_cache`
Inference cache with 384-dimensional dense vector support:
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique cache identifier |
| `query_text` | TEXT | Original user question |
| `response_text` | TEXT | Sanitized generic AI guidance |
| `embedding` | VECTOR(384) | MiniLM-L6-v2 dense embedding |
| `detected_mood` | VARCHAR(50) | Emotional context (e.g. sadness, anxiety) |
| `category` | VARCHAR(50) | Domain category |
| `similarity_threshold`| FLOAT | Minimum cosine similarity required (0.90) |
| `hit_count` | INTEGER | Total times this response served as cache hit |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `last_accessed_at` | TIMESTAMPTZ | Last cache hit timestamp |
| `expires_at` | TIMESTAMPTZ | TTL expiration date (default 30 days) |
| `is_active` | BOOLEAN | Active status flag |

**Vector Index**: HNSW index on `embedding` using `vector_cosine_ops` for fast nearest-neighbor lookups.

---

## Configuration Settings

Configured in `app/config.py` using `pydantic-settings`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5435/mindbridge"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    MINDBRIDGE_BASE_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    MINDBRIDGE_ADAPTER_ID: str = "aayush0K/Llama-3-MindBridge"
    INFERENCE_URL: str = "http://localhost:8001/generate"
    REMOTE_INFERENCE_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6380"
    MEMORY_TTL_SECONDS: int = 86_400
    SEMANTIC_CACHE_ENABLED: bool = True
    SEMANTIC_CACHE_THRESHOLD: float = 0.90
    SEMANTIC_CACHE_TTL_DAYS: int = 30
    CORS_ORIGINS: str = "http://localhost:3000"
    CORPUS_PATH: str = "./corpus/mental_health_corpus.json"
    APP_ENV: str = "development"
```

---

## Startup Sequence

FastAPI `lifespan` manager in `app/main.py`:
1. `Base.metadata.create_all` — ensures PostgreSQL tables (including `semantic_cache`) exist.
2. `embedder.initialize()` & `embedder.load_corpus()` — loads `all-MiniLM-L6-v2` and pre-computes corpus embeddings.
3. `classifier_service.initialize()` — loads classification model weights (non-fatal if absent).
4. `_initialize_inference()` — initializes HTTP client for Llama 3 8B remote GPU server.
5. `mood_detector.load()` — loads DistilBERT emotion detection pipeline.
6. `memory_service.initialize()` — establishes connection to Redis 7 (non-fatal fallback).
