from anthropic import AsyncAnthropic
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()


async def generate_deal_narrative(prompt: str) -> str:
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Anthropic is not configured')
    client = AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value())
    message = await client.messages.create(
        model='claude-3-5-sonnet-latest',
        max_tokens=700,
        messages=[{'role': 'user', 'content': f'Write a concise investor narrative for this FlipCycle deal: {prompt}'}],
    )
    return ''.join(block.text for block in message.content if hasattr(block, 'text'))
