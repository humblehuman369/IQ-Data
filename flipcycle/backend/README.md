# FlipCycle FastAPI Backend

This package is the FastAPI, PostgreSQL, Redis, and service-integration backend for the migrated FlipCycle monorepo. It is designed to be deployed separately from the Vercel-hosted Next.js frontend and exposed to the frontend through `NEXT_PUBLIC_API_BASE_URL`.

## Runtime services

The backend expects PostgreSQL 15 and Redis 7 in production. Set `DATABASE_URL` to an async psycopg connection string such as `postgresql+psycopg://user:password@host:5432/flipcycle` and set `REDIS_URL` to a Redis 7 endpoint. Optional service keys enable Stripe billing, Resend email, Anthropic AI narratives, AWS S3 document storage, and Sentry observability.

## Local commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pytest
```

The main product endpoints live under `/api`, matching the Next.js client contract: `/api/workspace/summary`, `/api/projects`, `/api/projects/{id}/expenses`, `/api/projects/{id}/comps`, `/api/projects/{id}/documents`, `/api/projects/{id}/collaborators`, and `/api/deals/calculate`.
