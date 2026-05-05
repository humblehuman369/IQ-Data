from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.auth.security import create_token, hash_password, new_totp_secret, verify_password, verify_totp
from app.db.session import get_session
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair, TotpSetupResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenPair)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> TokenPair:
    exists = await session.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')
    user = User(email=payload.email, name=payload.name, hashed_password=hash_password(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return TokenPair(access_token=create_token(str(user.id)), refresh_token=create_token(str(user.id), minutes=60 * 24 * 14))


@router.post('/login', response_model=TokenPair)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenPair:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password) or not verify_totp(user.totp_secret, payload.totp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return TokenPair(access_token=create_token(str(user.id)), refresh_token=create_token(str(user.id), minutes=60 * 24 * 14))


@router.post('/totp/setup', response_model=TotpSetupResponse)
async def setup_totp(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    secret = new_totp_secret()
    user.totp_secret = secret
    session.add(user)
    await session.commit()
    return TotpSetupResponse(secret=secret, provisioning_uri=f'otpauth://totp/FlipCycle:{user.email}?secret={secret}&issuer=FlipCycle')
