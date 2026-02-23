# Operations

## Local Development
- Backend: run `uvicorn app.main:app --reload`
- Frontend: run `npm run dev`

## Production Notes
- Set `CORS_ORIGINS` to restrict cross-origin access in production.
- Adjust `RATE_LIMIT_INGEST` and `RATE_LIMIT_UPLOAD` to tune traffic limits.
- Redis is required for multi-instance real-time streaming.
- Use `gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 app.main:app` for production ASGI workers.
- Use Alembic for migrations: `alembic revision --autogenerate -m "init"` then `alembic upgrade head`.
- For on-prem production, use `docker-compose.prod.yml` with `.env.prod`.

## Background Tasks (optional)
If you want async processing, run:
```bash
celery -A app.services.tasks worker --loglevel=info
```

## Live Feed Simulator (dev)
```bash
python backend/scripts/stream_simulator.py --api http://localhost:8000 --match match-001
```

## Storage
- Local: `storage/` in repo root
- Production: MinIO or S3 (configure via env)
