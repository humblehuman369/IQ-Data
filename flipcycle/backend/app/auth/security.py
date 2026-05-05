from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
import pyotp
from passlib.context import CryptContext
from app.core.config import get_settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str | None) -> bool:
    return bool(hashed_password and pwd_context.verify(password, hashed_password))


def create_token(subject: str, minutes: int | None = None) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.access_token_minutes)
    payload = {'sub': subject, 'exp': expires, 'iat': datetime.now(timezone.utc), 'jti': str(uuid4())}
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret.get_secret_value(), algorithms=[settings.jwt_algorithm])


def new_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str | None, code: str | None) -> bool:
    if not secret:
        return True
    if not code:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)
