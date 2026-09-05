# API Reference

MindBridge AI exposes a versioned REST API at `/api/v1` and a WebSocket endpoint at `/ws/chat`.

Interactive Swagger UI: **http://localhost:8000/docs**  
ReDoc: **http://localhost:8000/redoc**

---

## Authentication

All protected endpoints require a JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

Access tokens expire in **30 minutes**. Use the `/auth/refresh` endpoint to obtain a new one using your refresh token (valid for **30 days**).

---

## Auth Endpoints

### `POST /api/v1/auth/register`

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "StrongPass123!",
  "full_name": "Jane Doe"
}
```

**Response `201`:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "created_at": "2025-07-09T12:00:00Z"
  }
}
```

**Errors:**
- `409` — Email already registered

---

### `POST /api/v1/auth/login`

Authenticate an existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

**Response `200`:** Same structure as `/register`.

**Errors:**
- `401` — Invalid email or password
- `403` — Account is deactivated

---

### `POST /api/v1/auth/refresh`

Exchange a refresh token for a new access token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` — Invalid or expired refresh token

---

### `POST /api/v1/auth/logout`

Stateless logout — client should discard both tokens.

**Response `200`:**
```json
{ "message": "Logged out successfully" }
```

---

## User Endpoints

### `GET /api/v1/users/me` 🔒

Get the currently authenticated user's profile.

**Response `200`:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "created_at": "2025-07-09T12:00:00Z"
}
```

---

## Chat Endpoints

### `POST /api/v1/chat/message` 🔒

Send a user message and receive an AI response. This is the core endpoint.

**Request:**
```json
{
  "message": "I've been feeling really anxious lately.",
  "session_id": "uuid-or-null"
}
```

- `session_id`: If omitted or `null`, a new session is created automatically. Pass the `session_id` from the previous response to continue a conversation.
- `message`: Maximum 1000 characters.

**Response `200`:**
```json
{
  "response": "I hear you — anxiety can feel exhausting...",
  "session_id": "uuid",
  "is_crisis": false,
  "is_relevant": true,
  "relevance_score": 0.68,
  "few_shot_count": 3,
  "predicted_category": "anxiety",
  "classifier_confidence": 0.84,
  "uncertainty": 0.012,
  "memory_used": true,
  "detected_mood": "anxiety",
  "mood_confidence": 0.89,
  "cache_hit": false,
  "cached_similarity": 0.0
}
```

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `response` | string | AI-generated response text |
| `session_id` | UUID | Session to pass in subsequent messages |
| `is_crisis` | bool | True if crisis protocol was activated |
| `is_relevant` | bool | True if message passed relevance gate |
| `relevance_score` | float | Cosine similarity to mental health corpus (0–1) |
| `few_shot_count` | int | Number of examples retrieved for this response |
| `predicted_category` | string\|null | Classifier-predicted mental health category |
| `classifier_confidence` | float | Classifier confidence (0–1) |
| `uncertainty` | float | MC Dropout uncertainty (lower = more confident) |
| `memory_used` | bool | True if conversation history was injected |
| `detected_mood` | string\|null | DistilBERT detected emotion label |
| `mood_confidence` | float | Emotion detection confidence (0–1) |
| `cache_hit` | bool | True if served from PostgreSQL semantic cache (bypassed GPU) |
| `cached_similarity` | float | Cosine similarity score on semantic cache match (0–1) |

**Crisis response:**  
When `is_crisis=true`, `response` contains Indian national helpline numbers (Tele-MANAS `14416` / `1800-89-14416` and Emergency `112`). `few_shot_count` will be 0 and `cache_hit` will be false.

---

### `GET /api/v1/chat/cache-metrics` 🔒

Retrieve live performance metrics for Semantic Response Caching.

**Response `200`:**
```json
{
  "total_queries": 45,
  "cache_hits": 25,
  "cache_misses": 20,
  "gpu_calls_avoided": 25,
  "hit_rate_percentage": 55.56,
  "avg_cache_lookup_ms": 21.33,
  "avg_embedding_ms": 25.96,
  "avg_llama_inference_ms": 1420.5,
  "avg_hit_similarity_score": 0.965,
  "recent_samples_tracked": 45
}
```

---

### `GET /api/v1/chat/sessions` 🔒

List all chat sessions for the current user, newest first.

**Response `200`:** Array of session objects:
```json
[
  {
    "id": "uuid",
    "title": "I've been feeling really anxious...",
    "message_count": 6,
    "crisis_flagged": false,
    "started_at": "2025-07-09T12:00:00Z"
  }
]
```

---

### `GET /api/v1/chat/sessions/{session_id}/messages` 🔒

Get all messages in a session (in chronological order). Validates ownership.

**Response `200`:** Array of message objects:
```json
[
  {
    "id": "uuid",
    "session_id": "uuid",
    "role": "user",
    "content": "I feel anxious.",
    "relevance_score": 0.65,
    "is_crisis": false,
    "created_at": "2025-07-09T12:00:00Z"
  }
]
```

**Errors:**
- `404` — Session not found or not owned by current user

---

### `DELETE /api/v1/chat/sessions/{session_id}` 🔒

Delete a session and all its messages. Also clears the Redis memory for this session.

**Response `200`:**
```json
{ "message": "Session deleted" }
```

---

## Mood Endpoints

### `POST /api/v1/mood/log` 🔒

Log a mood entry.

**Request:**
```json
{
  "mood_score": 7,
  "mood_label": "calm",
  "notes": "Feeling better after journaling."
}
```

- `mood_score`: Integer 1–10 (required)
- `mood_label`: Free-text label (optional)
- `notes`: Free-text notes (optional)

**Response `201`:** The created mood log entry.

**Errors:**
- `422` — `mood_score` not in range 1–10

---

### `GET /api/v1/mood/history` 🔒

Get mood history for the past N days (default 30, max 365).

**Query params:** `?days=30`

**Response `200`:** Array of mood log entries, newest first.

---

### `GET /api/v1/mood/stats` 🔒

Get aggregated mood statistics for the last 30 days.

**Response `200`:**
```json
{
  "avg_score": 6.4,
  "most_common_label": "anxious",
  "trend": "improving",
  "total_logs": 14
}
```

- `trend`: `"improving"` | `"declining"` | `"stable"` (based on first-half vs second-half average)

---

## Journal Endpoints

### `POST /api/v1/journal` 🔒

Create a private reflective journal entry.

**Request:**
```json
{
  "title": "Evening Reflections",
  "content": "Spent time outside today and felt a noticeable lift in mood.",
  "mood_tag": "calm"
}
```

**Response `201`:** The created journal entry object (`id`, `user_id`, `title`, `content`, `mood_tag`, `created_at`, `updated_at`).

---

### `GET /api/v1/journal` 🔒

List user's journal entries (ordered newest first, up to 100 entries).

**Response `200`:** Array of journal entry objects.

---

### `GET /api/v1/journal/{entry_id}` 🔒

Retrieve a specific journal entry by ID.

---

### `DELETE /api/v1/journal/{entry_id}` 🔒

Delete a specific journal entry.

---

## Report Endpoints

### `POST /api/v1/reports/generate` 🔒

Generate an AI-driven wellness summary report for a given time window.

**Request:**
```json
{
  "report_type": "weekly",
  "days": 7
}
```

**Response `201`:**
```json
{
  "id": "uuid",
  "report_type": "weekly",
  "period_start": "2026-08-29T00:00:00Z",
  "period_end": "2026-09-05T00:00:00Z",
  "summary": "Over the past 7 days, your emotional wellbeing showed steady improvement...",
  "key_topics": ["work-life balance", "sleep hygiene"],
  "mood_analysis": { "predominant_mood": "calm", "avg_score": 7.2 },
  "recommendations": "Continue regular journaling and maintaining boundary times for work."
}
```

---

## System Endpoints

### `GET /health`

System health check. No authentication required.

**Response `200`:**
```json
{
  "status": "healthy",
  "embedder_loaded": true,
  "corpus_size": 1247,
  "classifier_loaded": true,
  "classifier_categories": ["anxiety", "depression", "..."],
  "redis_connected": true,
  "memory_ttl_hours": 24
}
```

---

## WebSocket

### `WS /ws/chat`

Real-time chat via WebSocket. Requires authentication token in the initial connection URL or first message.

See `backend/app/ws/chat_ws.py` for the full message protocol.

---

## Error Format

All error responses follow FastAPI's standard format:
```json
{
  "detail": "Human-readable error message"
}
```

Common HTTP status codes:
- `400` — Bad request / validation error
- `401` — Unauthorized (missing or invalid token)
- `403` — Forbidden (account deactivated)
- `404` — Resource not found
- `409` — Conflict (e.g. duplicate email)
- `422` — Unprocessable entity (schema validation failure)
- `500` — Internal server error
