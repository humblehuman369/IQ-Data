from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.workspace import SeedSampleDataResponse, WorkspaceSummary
from app.services.workspace import dashboard_summary, seed_sample_data

router = APIRouter(prefix='/workspace', tags=['workspace'])


@router.get('/summary', response_model=WorkspaceSummary, response_model_by_alias=True)
async def summary(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)) -> WorkspaceSummary:
    return await dashboard_summary(session, user)


@router.post('/seed-sample-data', response_model=SeedSampleDataResponse)
async def seed_samples(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)) -> SeedSampleDataResponse:
    return await seed_sample_data(session, user)
