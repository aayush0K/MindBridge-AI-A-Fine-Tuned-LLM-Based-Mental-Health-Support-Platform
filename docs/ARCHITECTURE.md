# Architecture

This document describes the internal architecture of MindBridge AI in engineering detail.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Next.js 14 Frontend                       │
│  pages: /  (login) · /register · /dashboard · /chat         │
│  state:  Zustand (chatStore)                                 │
│  forms:  React Hook Form + Zod                               │
│  charts: Recharts (mood trends)                              │
│  UI:     Tailwind CSS, Radix UI, Lucide icons                │
└─────────────────────────────┬────────────────────────────────┘
                              │  HTTPS / WSS
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ API Layer  (/api/v1/)                                  │  │
│  │   auth.py   → /auth/register  /auth/login  /auth/...  │  │
│  │   chat.py   → /chat/message  /chat/sessions  ...      │  │
│  │   mood.py   → /mood/log  /mood/history  /mood/stats   │  │
│  │   users.py  → /users/me                               │  │
│  │   chat_ws.py → /ws/chat  (WebSocket)                  │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Service Layer                                          │  │
│  │   ai_service.py        ← main orchestrator            │  │
│  │   embedder.py          ← MiniLM + corpus operations   │  │
│  │   classifier.py        ← PyTorch model definition     │  │
│  │   classifier_service.py← model loading + inference    │  │
│  │   crisis_service.py    ← keyword regex detection      │  │
│  │   memory_service.py    ← Redis conversation memory    │  │
│  │   auth_service.py      ← JWT + bcrypt                 │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Data Layer                                             │  │
│  │   database.py  ← SQLAlchemy async engine               │  │
│  │   models/      ← User, ChatSession, Message, MoodLog  │  │
│  │   migrations/  ← Alembic versioned schema              │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────┬─────────────────────────────┬────────────────┬─────┘
          │                             │                │
          ▼                             ▼                ▼
    PostgreSQL 16                    Redis 7        Google Gemini
    (persistent store)        (conversation memory)  (LLM generation)
```

---

## AI Pipeline (Step by Step)

Every call to `POST /api/v1/chat/message` runs the following pipeline inside `ai_service.process_message()`:

### Step 1 — Sanitise
- Strip whitespace, cap at 1000 characters.
- Empty message → return early with a prompt to say more.

### Step 2 — Embed
- Encode the message using `all-MiniLM-L6-v2` (384-dim normalized vector).
- This single vector is reused for all subsequent operations.

### Step 3 — Relevance Gate
- Cosine similarity against all corpus embeddings.
- Threshold: **0.25** (lowered from the paper's 0.4 — short phrases score lower against longer corpus text).
- Off-topic? The LLM still responds, but gently steers back to wellbeing topics.

### Step 3.5 — Classifier
- Run `MentalHealthClassifier.predict_with_confidence()` with **20 MC Dropout passes**.
- Returns `category`, `confidence`, `uncertainty`.
- **Trust guard**: if the message is < 4 words, the classifier result is discarded (confidence is deceptively high on "yes", "okay", etc.)

### Step 4 — Crisis Detection
Three independent layers. **Any single layer triggering activates crisis protocol.**

| Layer | Description |
|---|---|
| **Keyword** | `crisis_service.is_crisis_message()` — compiled regex, word-boundary matched, case-insensitive. 100% recall on known phrases. |
| **Embedding** | `embedder.check_crisis_embedding()` — cosine similarity to crisis corpus sub-embeddings ≥ **0.70**. |
| **Classifier** | Classifier predicted "crisis" AND confidence ≥ **0.75** AND uncertainty < **0.04** AND word count ≥ **4**. |

If crisis: persist user message, return `CRISIS_RESPONSE` (helpline numbers), stop.

### Step 5 — Few-shot Retrieval
- If classifier is trusted and confidence ≥ 0.55: retrieve top-3 examples **from the predicted category only**.
- Otherwise: retrieve top-3 from the full corpus by cosine similarity.
- Crisis examples are **always excluded** from few-shot generation (to prevent literal "CRISIS" leaks on Gemini errors).

### Step 6 — Build Prompt
- Static system prompt + static seed examples (built once at module load).
- Append dynamic few-shot examples from Step 5.
- Fetch last 12 messages from Redis (`memory_service.get_history()`).
- Fall back to PostgreSQL history when Redis unavailable.
- Append current user message as the final turn.

### Step 7 — Generate
- Single `_gemini_model.generate_content(full_messages)` call.
- Cached `GenerativeModel` object (initialized once at startup — not re-instantiated per request).
- On error: use safest available corpus example response (crisis examples filtered out).

### Step 8 — Persist
- Atomic `memory_service.append_turn()` — writes user + AI message in one Redis pipeline.
- Persist both messages to PostgreSQL via SQLAlchemy (audit trail).
- Update `ChatSession.message_count` and `crisis_flagged` via SQL (not Python) to avoid race conditions.

### Step 9 — Return
Enriched payload: `response`, `is_crisis`, `is_relevant`, `relevance_score`, `few_shot_count`, `predicted_category`, `classifier_confidence`, `uncertainty`, `memory_used`.

---

## Memory Engine

```
Per session: Redis List — key: "mb:memory:{session_id}"

Write (append_turn):
  RPUSH key user_json
  RPUSH key ai_json
  LTRIM key -20 -1    ← keep newest 20 messages (10 turns)
  EXPIRE key 86400    ← 24h TTL reset on every write
  (all 4 commands in a single pipeline — atomic)

Read (get_history):
  LRANGE key -12 -1   ← last 12 messages (6 turns for LLM)
```

**Fallback**: When Redis is unavailable (`_available = False`), `get_history()` returns `[]`. The chat API falls back to the PostgreSQL history loaded at request start. The LLM still responds with context; only the Redis rolling window is lost.

**Recovery**: On `ping()` success, `_available` is reset to `True` automatically.

---

## ML Classifier

**Model**: `MentalHealthClassifier` — 2 layers, ~28K parameters.

```
Input: 384-dim MiniLM embedding (frozen — not fine-tuned)
  │
  ├─ Linear(384 → 64) → ReLU → Dropout(p=0.5)
  │
  └─ Linear(64 → 10)
        │
        └─ Softmax → 10 category probabilities
```

**Categories**: `anxiety`, `depression`, `stress`, `sleep`, `loneliness`, `self_esteem`, `grief`, `anger`, `relationships`, `crisis`

**Training**: Feed-forward, CrossEntropyLoss, standard Adam optimizer. Training script is in `backend/scripts/train_classifier.py` (preserved for future retraining).

**Inference**: Monte Carlo Dropout — run 20 forward passes with dropout **active**, average the softmax outputs. This gives:
- `confidence`: mean max probability across passes
- `uncertainty`: variance of the predicted class probability across passes

**Graceful degradation**: If `backend/app/models/classifier_weights.pt` does not exist, `ClassifierService.initialize()` logs a warning and sets `_loaded = False`. All downstream code checks `classifier_result["available"]` before trusting any predictions.

---

## Database Schema

### `users`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `email` | TEXT (unique) | |
| `hashed_password` | TEXT | bcrypt |
| `full_name` | TEXT | nullable |
| `is_active` | BOOLEAN | default true |
| `created_at` | TIMESTAMPTZ | |

### `chat_sessions`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | Used as Redis memory key |
| `user_id` | UUID (FK → users) | |
| `title` | TEXT | First 50 chars of first message |
| `message_count` | INTEGER | incremented atomically via SQL |
| `crisis_flagged` | BOOLEAN | true if any message triggered crisis |
| `started_at` | TIMESTAMPTZ | |

### `messages`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `session_id` | UUID (FK → chat_sessions) | |
| `role` | TEXT | `user` or `assistant` |
| `content` | TEXT | |
| `relevance_score` | FLOAT | from embedder |
| `is_crisis` | BOOLEAN | |
| `created_at` | TIMESTAMPTZ | |

### `mood_logs`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → users) | |
| `mood_score` | INTEGER | 1–10 |
| `mood_label` | TEXT | e.g. "calm", "anxious" |
| `notes` | TEXT | nullable |
| `logged_at` | TIMESTAMPTZ | |

---

## Configuration

All settings are in `app/config.py` via `pydantic-settings`. Values are read from environment variables (via `.env` for local development).

```python
class Settings(BaseSettings):
    DATABASE_URL: str             # required
    JWT_SECRET_KEY: str           # required (no default)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    GEMINI_API_KEY: str           # required (no default)
    REDIS_URL: str = "redis://localhost:6380"
    MEMORY_TTL_SECONDS: int = 86_400
    CORS_ORIGINS: str = "http://localhost:3000"
    CORPUS_PATH: str = "./corpus/mental_health_corpus.json"
    APP_ENV: str = "development"
```

---

## Startup Sequence

`main.py` uses FastAPI's `lifespan` context manager:

1. `embedder.initialize()` — load `all-MiniLM-L6-v2` from disk/HuggingFace cache
2. `embedder.load_corpus()` — parse JSON, pre-compute all embeddings (startup cost)
3. `classifier_service.initialize()` — load `classifier_weights.pt` (non-fatal if missing)
4. `_initialize_gemini()` — configure Gemini API, cache `GenerativeModel` (non-fatal if no key)
5. `memory_service.initialize()` — connect to Redis (non-fatal if unavailable)

Each step is wrapped in `try/except` — a failed component logs an error and the server continues. The `/health` endpoint reports the status of each subsystem.
