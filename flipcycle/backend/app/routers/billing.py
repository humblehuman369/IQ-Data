from fastapi import APIRouter, Depends
from pydantic import BaseModel, AnyHttpUrl
from app.auth.dependencies import get_current_user
from app.models import User
from app.services.billing import create_checkout_session

router = APIRouter(prefix='/billing', tags=['billing'])


class CheckoutRequest(BaseModel):
    price_id: str
    success_url: AnyHttpUrl
    cancel_url: AnyHttpUrl


@router.post('/checkout')
async def checkout(payload: CheckoutRequest, user: User = Depends(get_current_user)):
    session = create_checkout_session(user.email or 'buyer@flipcycle.app', payload.price_id, str(payload.success_url), str(payload.cancel_url))
    return {'id': session.id, 'url': session.url}
