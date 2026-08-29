# Deployment Guide

This guide covers deploying MindBridge AI to a production server.

> **Before you deploy**: read [SECURITY.md](../SECURITY.md) and ensure you have generated strong secrets for `JWT_SECRET_KEY`.

---

## Prerequisites

- A Linux server (Ubuntu 22.04 LTS recommended)
- Docker Engine 24+ and Docker Compose v2
- A domain name with DNS configured (for HTTPS)
- A Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/mindbridge-ai.git
cd mindbridge-ai
```

---

## 2. Configure Environment Variables

### Backend

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<STRONG_PASSWORD>@localhost:5435/mindbridge
JWT_SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(48))">
GEMINI_API_KEY=<your-gemini-api-key>
REDIS_URL=redis://localhost:6380
CORS_ORIGINS=https://your-domain.com
APP_ENV=production
```

### Frontend

```bash
cp frontend/.env.local.example frontend/.env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WS_URL=wss://api.your-domain.com
```

---

## 3. Update docker-compose.yml for Production

For production, use strong passwords for PostgreSQL:

```yaml
environment:
  POSTGRES_PASSWORD: <strong-db-password>
```

Ensure Redis persistence is enabled (it is by default via `--appendonly yes`).

---

## 4. Start Infrastructure

```bash
docker compose up -d
```

Verify services are healthy:
```bash
docker compose ps
```

---

## 5. Deploy the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start with production settings (use gunicorn for multi-worker)
pip install gunicorn
gunicorn app.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

For process management, use systemd or supervisord:

```ini
# /etc/systemd/system/mindbridge-backend.service
[Unit]
Description=MindBridge AI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/mindbridge-ai/backend
Environment=PATH=/home/ubuntu/mindbridge-ai/backend/venv/bin
ExecStart=/home/ubuntu/mindbridge-ai/backend/venv/bin/gunicorn app.main:app \
  --workers 2 --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable mindbridge-backend
sudo systemctl start mindbridge-backend
```

---

## 6. Deploy the Frontend

```bash
cd frontend
npm install
npm run build
npm start  # or use pm2
```

With pm2:
```bash
npm install -g pm2
pm2 start npm --name "mindbridge-frontend" -- start
pm2 save
pm2 startup
```

---

## 7. Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/mindbridge
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend docs
    location /docs { proxy_pass http://localhost:8000/docs; }
    location /health { proxy_pass http://localhost:8000/health; }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
}
```

Use [Certbot](https://certbot.eff.org/) for free TLS certificates from Let's Encrypt.

---

## 8. Verify Deployment

```bash
curl https://your-domain.com/health
```

Expected:
```json
{
  "status": "healthy",
  "embedder_loaded": true,
  "redis_connected": true,
  ...
}
```

---

## Health Monitoring

The `/health` endpoint reports the status of all subsystems. Use it with:
- **Uptime Kuma** or **Betteruptime** for availability monitoring
- **Prometheus + Grafana** for metrics (add `prometheus-fastapi-instrumentator` to `requirements.txt`)

---

## Backups

### PostgreSQL
```bash
# Daily backup
docker exec mindbridge-db pg_dump -U postgres mindbridge > backup_$(date +%Y%m%d).sql
```

### Redis
Redis uses AOF persistence by default — the `mindbridge_redisdata` volume is persistent. Back up the volume periodically.

---

## Notes

- **Redis TTL**: Conversation memory expires after 24 hours of inactivity. This is by design. No manual cleanup is needed.
- **Gemini quota**: The free Gemini tier has rate limits (RPM). If you hit 429 errors, the backend gracefully falls back to corpus examples. For production, use a paid tier.
- **Classifier weights**: `backend/app/models/classifier_weights.pt` must be present. It is committed to the repository (103 KB). If it is absent, the system falls back to cosine-similarity-only retrieval — crisis keyword detection still works.
