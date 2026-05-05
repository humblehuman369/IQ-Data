import resend
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()
if settings.resend_api_key:
    resend.api_key = settings.resend_api_key.get_secret_value()


def send_email(to: str, subject: str, html: str):
    if not settings.resend_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Resend is not configured')
    return resend.Emails.send({'from': 'FlipCycle <notifications@flipcycle.app>', 'to': [to], 'subject': subject, 'html': html})
