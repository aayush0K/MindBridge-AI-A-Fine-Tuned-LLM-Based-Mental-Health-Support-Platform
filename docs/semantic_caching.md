# ⚡ Semantic Response Caching in MindBridge AI

## 1. Overview & Architecture

MindBridge AI incorporates an inference-time **Semantic Response Cache** to optimize inference latency, reduce expensive remote GPU compute on Google Colab / cloud nodes, and provide sub-50ms response times for common, repetitive mental wellness inquiries.

Rather than executing an exact string lookup, the semantic cache leverages dense vector embeddings to match user inquiries that share the same underlying semantic intent, even when phrased differently.

```text
User Query
    │
    ▼
FastAPI `/api/v1/chat/message`
    │
    ▼
[Step 1] Input Sanitization
    │
    ▼
[Step 2] MiniLM (384-dim) Dense Vector Embedding
    │
    ▼
[Step 3] DistilBERT Mood / Emotion Detection & Relevance Check
    │
    ▼
[Step 4] SAFETY & CRISIS EVALUATION (Keyword + Embedding + Classifier)
    │
    ├──► [CRISIS TRIGGERED] ──► Immediate CRISIS_RESPONSE + Tele-MANAS (14416 / 112)
    │                           ⛔ STOP — NEVER CONSULT CACHE, NEVER CALL GPU
    │
    ▼ [SAFE QUERY]
[Step 4.7] SEMANTIC CACHE LOOKUP (PostgreSQL + pgvector)
    │  - Cosine similarity query against active unexpired cache rows
    │  - Mood / Emotional Context compatibility guard
    │
    ├──► [SIMILARITY >= 0.90 & MOOD COMPATIBLE]
    │       │
    │       └──► ⚡ CACHE HIT!
    │            - Update hit_count & last_accessed_at
    │            - Record metrics (GPU call avoided, latency, hit rate)
    │            - Persist turn to Redis conversation memory
    │            - Return cached guidance directly (0ms GPU inference)
    │
    ▼ [CACHE MISS / SIMILARITY < 0.90]
[Step 5 & 6] Dynamic Few-Shot Retrieval & History Assembly
    │
    ▼
[Step 7] Remote GPU Inference Server (Meta Llama 3 8B + MindBridge LoRA)
    │
    ▼
[Step 7.5] Output Safety Sanitizer (Foreign hotline & clinical claim stripper)
    │
    ▼
[Step 7.8] Cache Eligibility Evaluation
    │  - PII Detection (blocks personal names, emails, phones, addresses)
    │  - Reusable Guidance Quality Validation
    │  - Near-Duplicate Prevention (> 0.98 similarity check)
    │  - Persist to PostgreSQL `semantic_cache` table with 30-day TTL
    │
    ▼
[Step 8] Persist Turn to Redis Memory & PostgreSQL Messages Audit Table
    │
    ▼
[Step 9] Return Enriched Response Payload
```

---

## 2. Safety-First Design Principle

Mental health conversational agents must adhere to strict clinical and ethical safety boundaries:

1. **Deterministic Safety Priority:** Safety and crisis detection is evaluated **first**. If a message contains crisis markers, self-harm language, or suicidal ideation, execution immediately halts and returns emergency hotlines (Tele-MANAS `14416` / Emergency `112`). The semantic cache is **never** consulted.
2. **Crisis Paraphrase Shield:** Even if a crisis query is semantically similar to a cached coping exercise, the crisis detector takes precedence and halts the request before the cache lookup stage.
3. **No Emergency Caching:** Emergency responses, hotline notices, or system error messages are explicitly blocked from being stored in the cache by the `is_reusable_guidance()` filter.
4. **Mood & Context Compatibility:** A cached guidance generated for a joyful state is guarded from being returned to a user experiencing acute sadness or explosive anger.

---

## 3. Technology Stack & Roles

| Component | Technology | Responsibility |
|---|---|---|
| **Vector Embedding** | `sentence-transformers/all-MiniLM-L6-v2` | Computes 384-dimensional dense semantic vectors for queries. Shared singleton instance across pipeline. |
| **Persistent Vector Store** | PostgreSQL 16 + `pgvector` | Stores embeddings in `VECTOR(384)` column; accelerates nearest-neighbor search via HNSW vector index (`vector_cosine_ops`). |
| **Short-Term Context** | Redis 7 | Maintains 24h rolling multi-turn conversational history. Caching a response does **not** bypass updating Redis memory. |
| **PII & Privacy Engine** | `app.safety.pii_filter` | Regular expressions and heuristic rules inspecting text for phone numbers, emails, locations, and personal disclosures. |
| **Performance Tracking** | `app.services.metrics_service` | Thread-safe in-memory metrics collecting lookup latency, embedding latency, hit counts, miss counts, and avoided GPU compute. |

---

## 4. Privacy & PII Protection Rules

To protect user confidentiality, responses are only stored in the shared semantic cache if they meet strict criteria:
- **No Email Addresses:** Matched via RFC-compliant email regex.
- **No Phone Numbers:** Matched via US and Indian 10-digit telephone patterns.
- **No Physical Addresses:** Matched via street keywords and 5/6 digit postal codes.
- **No Identity Disclosures:** Flags phrases such as `"my name is [Name]"`, `"call me [Name]"`, `"my husband [Name]"`.
- **No Specific Prescription Disclosures:** Flags dosage specifics (e.g. `"prescribed me 20mg"`).
- **Quality Length Bounds:** Responses must be between 30 and 2000 characters.

---

## 5. Configuration Settings

Environment variables in `backend/.env`:

```env
# ── SEMANTIC RESPONSE CACHE ──────────────────────────────────
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_THRESHOLD=0.90
SEMANTIC_CACHE_TTL_DAYS=30
```

- `SEMANTIC_CACHE_ENABLED`: Toggles semantic caching on/off system-wide. When `false`, the pipeline routes all requests directly to Llama 3 8B.
- `SEMANTIC_CACHE_THRESHOLD`: Minimum cosine similarity (range `0.0` to `1.0`) required to trigger a cache hit. Defaults to `0.90`.
- `SEMANTIC_CACHE_TTL_DAYS`: Cache entry lifetime in days before automatic expiration. Defaults to `30`.

---

## 6. Database Migration & Schema

### PostgreSQL Table Schema (`semantic_cache`)

```sql
CREATE TABLE semantic_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,
    detected_mood VARCHAR(50),
    category VARCHAR(50),
    similarity_threshold FLOAT NOT NULL DEFAULT 0.90,
    hit_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    last_accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- HNSW Vector Index for Cosine Distance
CREATE INDEX ix_semantic_cache_embedding_hnsw 
ON semantic_cache USING hnsw (embedding vector_cosine_ops);

-- Index for TTL queries and active status
CREATE INDEX ix_semantic_cache_expires_at ON semantic_cache (expires_at);
CREATE INDEX ix_semantic_cache_is_active ON semantic_cache (is_active);
```

### Migration Execution

To apply the migration using Alembic:
```bash
cd backend
alembic upgrade head
```

---

## 7. Metrics & Live Monitoring

Real-time cache performance is accessible via REST API:

```http
GET /api/v1/chat/cache-metrics
```

### Example JSON Response:
```json
{
  "total_queries": 42,
  "cache_hits": 28,
  "cache_misses": 14,
  "gpu_calls_avoided": 28,
  "hit_rate_percentage": 66.67,
  "avg_cache_lookup_ms": 21.33,
  "avg_embedding_ms": 25.96,
  "avg_llama_inference_ms": 1850.40,
  "avg_hit_similarity_score": 0.9793,
  "recent_samples_tracked": 42
}
```

---

## 8. Automated Testing

MindBridge AI includes 12 automated unit and integration tests covering the complete caching lifecycle:

```bash
cd backend
.\venv\Scripts\pytest tests/test_semantic_cache.py -v
```

### Test Coverage Breakdown:
1. `test_same_question_twice_hits_cache` — Verifies second request hits cache and does not call GPU.
2. `test_paraphrased_question_hits_cache` — Verifies paraphrased queries with similarity &ge; 0.90 trigger cache hits.
3. `test_unrelated_question_misses_cache` — Verifies unrelated queries trigger cache misses and route to Llama.
4. `test_crisis_question_safety_intercepts` — Verifies crisis detector halts request before cache lookup.
5. `test_crisis_similar_to_cached_query_safety_wins` — Verifies safety priority even when query resembles cached text.
6. `test_mood_compatibility_checks` — Verifies conflicting emotional contexts (e.g. distress vs. joy) are rejected.
7. `test_pii_detection_and_rejection` — Verifies emails, phone numbers, and names are blocked from cache.
8. `test_unsafe_response_rejected_from_cache` — Verifies model errors and crisis hotlines are never cached.
9. `test_expired_cache_is_ignored` — Verifies entries past TTL are omitted from candidate selection.
10. `test_cache_failure_graceful_fallback` — Verifies database disconnects fall back to Llama without crashing.
11. `test_minilm_failure_graceful_fallback` — Verifies embedding exceptions fall back gracefully.
12. `test_remote_gpu_failure_preserves_error_message` — Verifies friendly server notice is preserved if GPU is down.

### Live End-to-End Verification Script:
```bash
cd backend
python scripts/test_semantic_cache_live.py
```
