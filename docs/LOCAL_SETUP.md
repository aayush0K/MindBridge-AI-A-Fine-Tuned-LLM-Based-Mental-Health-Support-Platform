# Local setup — environment variables

## Do you need `.env`?

| File | Required? | Notes |
|------|-----------|--------|
| `backend/.env` | **Yes** (file exists) | DB + JWT must match your Postgres. Gemini is optional for first run. |
| `frontend/.env.local` | **Yes** (already set) | Points to `http://localhost:8000` — no API keys on frontend. |

## Where to get each value

### `DATABASE_URL` (required)

**Default (no change if using Docker):**

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5435/mindbridge
```

- **Source:** `docker-compose.yml` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)
- **Start DB:** Open **Docker Desktop**, then run `docker compose up -d` from project root
- **Port 5435:** Used because Windows may already run PostgreSQL on 5432/5433

If you use local Postgres without Docker, set user/password/db to match your install.

---

### `JWT_SECRET_KEY` (required)

- **Local dev:** Already set in `.env` — you can keep it as-is.
- **Production:** Generate a long random string:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

---

### `GEMINI_API_KEY` (optional for local testing)

- **Get it:** [Google AI Studio → API keys](https://aistudio.google.com/app/apikey)
  1. Sign in with Google
  2. Click **Create API key**
  3. Paste into `backend/.env` → `GEMINI_API_KEY=...`
- **Without key:** Backend still runs; chat uses a **fallback** message instead of real Gemini replies. Crisis detection and relevance filtering still work.

---

### Frontend (`frontend/.env.local`)

Already configured — no secrets:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Run order

```powershell
# 1. Start Docker Desktop, then:
cd c:\mindbridge
docker compose up -d

# 2. Backend
cd backend
.\venv\Scripts\activate
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm run dev
```

Open http://localhost:3000
