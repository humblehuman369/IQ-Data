# FlipCycle Monorepo

FlipCycle has been converted into a two-package monorepo with a **Next.js 16 / React 19 TypeScript frontend** and a **FastAPI / PostgreSQL / Redis backend**. The frontend package is ready for Vercel-oriented workflows, while the backend package is structured for a Python ASGI deployment behind a managed PostgreSQL 15 database and Redis 7 instance.

| Area | Location | Primary Runtime | Purpose |
|---|---:|---:|---|
| Frontend | `frontend/` | Next.js 16, React 19, Tailwind CSS | Investor dashboard, deal analyzer, comps, budget, documents, collaborators, map panel, analytics, and mobile wrapper configuration. |
| Backend | `backend/` | FastAPI, Uvicorn/Gunicorn, SQLAlchemy 2 async | API contracts, authentication primitives, billing, email, AI narrative, S3 uploads, exports, metrics, logging, and Alembic migrations. |
| Shared project controls | repository root | pnpm scripts | Developer commands that proxy common frontend workflows. |

## Local frontend workflow

Install JavaScript dependencies from the root or from `frontend/`, then run the Next.js development server. The frontend uses sample FlipCycle data when `NEXT_PUBLIC_API_BASE_URL` is not configured, which keeps the migrated interface reviewable before a live FastAPI service is provisioned.

```bash
pnpm install
pnpm dev
pnpm test
pnpm check
pnpm build
```

## Local backend workflow

Create a Python virtual environment inside `backend/`, install backend dependencies, configure PostgreSQL and Redis URLs, then run migrations and start FastAPI.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pytest
```

## Environment variables

| Variable | Package | Required | Description |
|---|---:|---:|---|
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Production | Base URL for the FastAPI backend, for example `https://api.example.com`. |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Frontend | Map features | API key used by `@vis.gl/react-google-maps` in deployments outside the Manus proxy environment. |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Frontend | Billing UI | Publishable key used by Stripe.js. |
| `DATABASE_URL` | Backend | Yes | PostgreSQL connection string, normalized by the backend to the async psycopg dialect. |
| `REDIS_URL` | Backend | Yes | Redis endpoint for rate limiting, cache, and token blacklist use cases. |
| `JWT_SECRET` | Backend | Yes | Secret used to sign API tokens. |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Backend | Billing | Stripe billing configuration. |
| `RESEND_API_KEY` | Backend | Email | Transactional email configuration. |
| `ANTHROPIC_API_KEY` | Backend | AI narrative | AI narrative generation configuration. |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET` | Backend | Document storage | S3 upload configuration. |
| `SENTRY_DSN` | Both | Observability | Frontend and backend error reporting DSN. |

## Deployment notes

The frontend includes `frontend/vercel.json` with `iad1` as the target region and is designed for Vercel deployment. Manus also provides built-in hosting and custom domain support; if you proceed with Vercel for the frontend, keep the backend deployed separately and set `NEXT_PUBLIC_API_BASE_URL` to that backend origin. The backend should be deployed to an ASGI-compatible Python host with PostgreSQL 15, Redis 7, and secure environment variables.

## Validation status

The repository includes Vitest tests for the frontend calculation contract and pytest tests for the backend calculation service. These tests are intentionally focused on migrated business logic so that the deal analyzer remains consistent across TypeScript and Python implementations.
