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
  "memory_used": true
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

**Crisis response:**  
When `is_crisis=true`, `response` contains helpline numbers (India + international). `few_shot_count` will be 0.

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
