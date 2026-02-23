# SkyBlueAI: Football Intelligence Suite

This repository contains a full-stack MVP implementation of the SkyBlueAI platform described in the PRD/SRS.

## What You Get
- FastAPI backend with ingestion, analysis, and simulation endpoints
- Celery task pipeline (optional) with Redis
- PostgreSQL-ready data layer (SQLite for local dev)
- React + Tailwind frontend with dashboard UI
- D3 heatmap and a minimal Three.js set-piece visualization
- Documentation for API, data contracts, and architecture

## Quick Start (Local)

### 1) Backend
```bash
cd /Users/hitarthdesai/Downloads/man\ city/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

### 2) Frontend
```bash
cd /Users/hitarthdesai/Downloads/man\ city/frontend
cp .env.example .env
npm install
npm run dev
```

### 3) (Optional) Docker Compose
```bash
cd /Users/hitarthdesai/Downloads/man\ city
docker compose up --build
```

### 4) Production (On-Prem)
```bash
cd /Users/hitarthdesai/Downloads/man\ city
cp .env.prod.example .env.prod
docker compose -f docker-compose.prod.yml up --build -d
```

## Notes
- For real CV/ML models, plug into `app/services` interfaces.
- This MVP uses deterministic heuristics for insights to keep it runnable.
- Sample event data is available at `storage/events/sample_events.json`.
- PostgreSQL driver uses `psycopg` (v3). Docker Compose already points to `postgresql+psycopg://`.
- Real-time updates are delivered over WebSocket at `/ws/match/{id}` using Redis pubsub when available.
- A dev live-feed simulator is available at `backend/scripts/stream_simulator.py`.
- See `docs/production.md` for on-prem production guidance.

## Repo Structure
```
backend/        FastAPI + services + data layer
frontend/       React + Tailwind UI
docs/           Architecture, API, and data contracts
storage/        Local storage for uploads (dev)
```

## Sales Materials
- `docs/sales/one_pager.md`
- `docs/sales/pricing.md`
- `docs/sales/implementation_plan.md`
- `docs/sales/roi.md`
- `docs/sales/security_questionnaire.md`
- `docs/sales/sla.md`
- `docs/sales/demo_script.md`
- `docs/product_readiness.md`

## Environment
Use `.env.example` as a starting point for configuration.
