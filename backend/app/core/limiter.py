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
            retry_after = max(ttl, 1)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit",
                    "message": "Слишком много запросов. Подожди немного.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Rate limit check failed (allowing request): %s", e)


# QA-035/036: the hourly quota above doesn't stop a burst of near-simultaneous
# requests from the same user — each one still reaches the LLM and holds a DB
# connection for the full stream duration, so a handful fired back-to-back was
# enough to queue up and stall. This caps a user to one in-flight AI generation
# per endpoint; a repeat while one is still running gets a clean 429 instead of
# piling onto the same resources.
async def check_not_in_flight(user_id: str, endpoint: str, ttl: int = 90) -> None:
    key = f"inflight:{endpoint}:{user_id}"
    try:
        acquired = await _redis.set(key, "1", ex=ttl, nx=True)
        if not acquired:
            remaining = await _redis.ttl(key)
            retry_after = max(remaining, 1)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "already_in_flight",
                    "message": "Предыдущий запрос ещё обрабатывается. Подожди немного.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("In-flight check failed (allowing request): %s", e)


async def release_in_flight(user_id: str, endpoint: str) -> None:
    key = f"inflight:{endpoint}:{user_id}"
    try:
        await _redis.delete(key)
    except Exception as e:
        logger.warning("Failed to release in-flight lock: %s", e)
