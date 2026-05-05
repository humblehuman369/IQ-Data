import stripe
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key.get_secret_value()


def ensure_stripe() -> None:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stripe is not configured')


def create_checkout_session(customer_email: str, price_id: str, success_url: str, cancel_url: str):
    ensure_stripe()
    return stripe.checkout.Session.create(mode='subscription', customer_email=customer_email, line_items=[{'price': price_id, 'quantity': 1}], success_url=success_url, cancel_url=cancel_url)
