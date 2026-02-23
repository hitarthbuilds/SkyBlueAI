# Production (On-Prem)

This setup is designed for on-prem (no cloud) using Docker Compose. It includes backend, frontend, Postgres, Redis, and MinIO.

## 1) Configure Environment
Copy `.env.prod.example` to `.env.prod` and set secure values:
- `JWT_SECRET`
- `CORS_ORIGINS`: e.g. `http://your-host:8080`
Front-end build uses `frontend/.env.production` (defaults to `/api`).

## 2) Build and Run
```bash
cd /Users/hitarthdesai/Downloads/man\ city
cp .env.prod.example .env.prod

docker compose -f docker-compose.prod.yml up --build -d
```

Frontend will be available at `http://<host>:8080`.

## 3) Migrations
```bash
docker compose -f /Users/hitarthdesai/Downloads/man\ city/docker-compose.prod.yml exec backend alembic upgrade head
```

## 4) Real-Time Feed
Ingest events with your provider or use the simulator:
```bash
python backend/scripts/stream_simulator.py --api http://<host>:8080/api --match match-001
```

## 5) Health Checks
- `/health`
- `/ready`

## 6) Security Notes
- Do not expose Redis/MinIO/Postgres publicly.
- Restrict `CORS_ORIGINS` to your host.
