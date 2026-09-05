# Local Setup — Environment & Running Guide

## Environment Files

| File | Required? | Purpose |
|------|-----------|---------|
| `backend/.env` | **Yes** | PostgreSQL connection, Redis, JWT secret, Inference URL, and Semantic Cache parameters. |
| `frontend/.env.local` | **Yes** | Points to `http://localhost:8000` — client API URL (no private secrets). |

---

## Configuration Variables Explained

### 1. `DATABASE_URL` (Required)

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5435/mindbridge
```

- **Database Engine:** PostgreSQL 16 with `pgvector` extension (container `mindbridge-db`).
- **Port 5435:** Port mapped on host in `docker-compose.yml` to prevent conflict with any native PostgreSQL running on 5432.
- **Start Container:** Open **Docker Desktop**, then run `docker compose up -d` from the repository root.

---

### 2. `REDIS_URL` (Required)

```env
REDIS_URL=redis://localhost:6380
```

- **Redis Engine:** Redis 7-Alpine with AOF persistence (container `mindbridge-redis`).
- **Port 6380:** Port mapped on host in `docker-compose.yml`. Used for rolling 24h conversation context.

---

### 3. `JWT_SECRET_KEY` (Required)

- **Local dev:** Already configured in `backend/.env`.
- **Production:** Generate a secure random string:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

---

### 4. `INFERENCE_URL` (Llama 3 8B + LoRA Remote GPU Server)

```env
INFERENCE_URL=http://localhost:8001/generate
```

- Points to your GPU inference server running `Meta-Llama-3-8B-Instruct` with the fine-tuned MindBridge LoRA adapter (`aayush0K/Llama-3-MindBridge`).
- For Google Colab Tesla T4 execution, set this to your active ngrok tunnel URL:
  ```env
  INFERENCE_URL=https://<your-ngrok-subdomain>.ngrok-free.dev/generate
  ```
- If the GPU server is offline, the backend gracefully falls back without crashing.

---

### 5. Semantic Response Cache Configuration

```env
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_THRESHOLD=0.90
SEMANTIC_CACHE_TTL_DAYS=30
```

- Bypasses remote GPU invocation for common inquiries matching previous responses with cosine similarity &ge; 0.90.
- Preserves privacy (rejects PII) and checks mood compatibility before returning cached responses.

---

### 6. Frontend Configuration (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Step-by-Step Run Instructions

### Step 1: Start Docker Infrastructure
Ensure **Docker Desktop** is running, then execute:

```powershell
docker compose up -d
docker ps
```
Verify `mindbridge-db` (port 5435) and `mindbridge-redis` (port 6380) show as healthy.

---

### Step 2: Start Backend Server

```powershell
cd backend
.\venv\Scripts\activate
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
- API Documentation: **http://localhost:8000/docs**
- Health Check: **http://localhost:8000/health**
- Cache Metrics: **http://localhost:8000/api/v1/chat/cache-metrics**

---

### Step 3: Start Frontend Server (In a separate terminal)

```powershell
cd frontend
npm run dev
```
Open **http://localhost:3000** in your browser.
