from fastapi import APIRouter
from app.schemas.workspace import DealInput, DealMetrics
from app.services.calculations import calculate_deal

router = APIRouter(prefix='/deals', tags=['deals'])


@router.post('/calculate', response_model=DealMetrics, response_model_by_alias=True)
async def calculate_deal_endpoint(input: DealInput) -> DealMetrics:
    return calculate_deal(input)
