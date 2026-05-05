# FlipCycle Environment Configuration

This document lists the runtime configuration expected by the migrated stack. Do not commit real secret values. Use the hosting provider's encrypted environment variable manager for deployment and a local untracked `.env` file for development.

| Variable | Package | Description |
|---|---:|---|
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Public origin for the FastAPI backend. |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Frontend | Browser Google Maps key for `@vis.gl/react-google-maps` outside managed proxy environments. |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Frontend | Stripe.js publishable key. |
| `SENTRY_DSN` | Frontend and backend | Optional error reporting DSN. |
| `DATABASE_URL` | Backend | PostgreSQL 15 connection string. The backend normalizes `postgresql://` URLs to `postgresql+psycopg://`. |
| `REDIS_URL` | Backend | Redis 7 endpoint for cache, rate limiting, and token blacklist use cases. |
| `JWT_SECRET` | Backend | Long random signing secret for JSON Web Tokens. |
| `STRIPE_SECRET_KEY` | Backend | Stripe secret key for checkout and billing APIs. |
| `STRIPE_WEBHOOK_SECRET` | Backend | Stripe webhook signing secret. |
| `RESEND_API_KEY` | Backend | Resend transactional email key. |
| `ANTHROPIC_API_KEY` | Backend | Anthropic API key for deal narrative generation. |
| `AWS_ACCESS_KEY_ID` | Backend | AWS access key for S3 document uploads. |
| `AWS_SECRET_ACCESS_KEY` | Backend | AWS secret access key for S3 document uploads. |
| `AWS_REGION` | Backend | AWS region, for example `us-east-1`. |
| `S3_BUCKET` | Backend | S3 bucket used for project documents. |

## Local development pattern

Create local `.env` files manually and keep them untracked. For the frontend, variables must be available to Next.js at build time. For the backend, variables are read through Pydantic Settings in `backend/app/core/config.py`.
