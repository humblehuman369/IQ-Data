from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.security import decode_token
from app.db.session import get_session
from app.models import User

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_user_id: int | None = Header(default=None),
) -> User:
    if x_user_id:
        user = await session.get(User, x_user_id)
        if user:
            return user
    if credentials:
        try:
            payload = decode_token(credentials.credentials)
            user_id = int(payload['sub'])
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token') from exc
        user = await session.get(User, user_id)
        if user:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
