import logging

import redis.asyncio as aioredis
from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
)


async def check_rate_limit(
    user_id: str,
    tier: str,
    endpoint: str,
    free_limit: int,
    pro_limit: int,
    window: int = 3600,
) -> None:
    limit = pro_limit if tier == "pro" else free_limit
    key = f"rl:{endpoint}:{user_id}"
    r = aioredis.from_url(settings.redis_url)
    try:
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window)
        ttl = await r.ttl(key)
        if count > limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit",
                    "message": "Слишком много запросов. Подожди немного."
                        if True else "Too many requests. Please wait.",
                    "retry_after": max(ttl, 1),
                },
            )
    finally:
        await r.close()
