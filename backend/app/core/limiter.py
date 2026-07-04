import logging

import redis.asyncio as aioredis
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

# Shared connection pool — a new TCP connection per rate-limit check does not scale
_redis = aioredis.from_url(settings.redis_url, max_connections=20)


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
    try:
        count = await _redis.incr(key)
        if count == 1:
            await _redis.expire(key, window)
        ttl = await _redis.ttl(key)
        if count > limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit",
                    "message": "Слишком много запросов. Подожди немного.",
                    "retry_after": max(ttl, 1),
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Rate limit check failed (allowing request): %s", e)
