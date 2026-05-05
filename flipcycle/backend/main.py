import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.routers import ai, auth, billing, deals, email, projects, workspace

settings = get_settings()
configure_logging()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment, traces_sample_rate=0.1)

app = FastAPI(title=settings.app_name, version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

for router in [deals.router, workspace.router, projects.router, auth.router, billing.router, email.router, ai.router]:
    app.include_router(router, prefix=settings.api_prefix)

Instrumentator().instrument(app).expose(app, endpoint='/metrics')


@app.get('/healthz')
async def healthz() -> dict[str, str]:
    return {'status': 'ok', 'service': 'flipcycle-api'}
