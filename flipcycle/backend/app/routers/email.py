from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from app.auth.dependencies import get_current_user
from app.models import User
from app.services.email import send_email

router = APIRouter(prefix='/email', tags=['email'])


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    html: str


@router.post('/send')
async def send(payload: EmailRequest, _: User = Depends(get_current_user)):
    return send_email(payload.to, payload.subject, payload.html)
