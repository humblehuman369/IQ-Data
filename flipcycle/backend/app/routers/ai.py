from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.models import User
from app.services.ai import generate_deal_narrative

router = APIRouter(prefix='/ai', tags=['ai'])


class NarrativeRequest(BaseModel):
    prompt: str


@router.post('/deal-narrative')
async def deal_narrative(payload: NarrativeRequest, _: User = Depends(get_current_user)):
    return {'narrative': await generate_deal_narrative(payload.prompt)}
