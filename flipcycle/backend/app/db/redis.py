from redis.asyncio import Redis
from app.core.config import get_settings

_settings = get_settings()
redis_client = Redis.from_url(_settings.redis_url, decode_responses=True)


async def blacklist_token(jti: str, expires_in_seconds: int) -> None:
    await redis_client.setex(f'token-blacklist:{jti}', expires_in_seconds, '1')


async def is_token_blacklisted(jti: str) -> bool:
    return bool(await redis_client.get(f'token-blacklist:{jti}'))
