"""Caches AI-generated interpretation text for endpoints whose input is
fully deterministic — the same birth date(s)/points always produce the same
prompt, so a repeat view of an already-seen reading was silently paying for
a fresh LLM call every single time, for text that could only ever come out
semantically identical. Confirmed with the product owner (2026-08-xx):
Matrix (base points, karmic tail, money line, children's matrix,
compatibility), Numerology's core/square/karmic sections, and
Compatibility's per-type interpretation all had this gap.

Deliberately NOT used for anything time-varying — Numerology's "forecast"
section (personal year/month/day) and any future "today"-keyed content
must keep calling the LLM live every time; see each call site's comment.

Cache keys embed the actual deterministic INPUT VALUES (birth dates, not
user/child/partner ids) rather than the owning entity's id. Two people who
happen to share a birth date get the same cached reading — a deliberate,
free efficiency win, not a bug — and if a profile's birth date is ever
corrected, the new date is simply a cache miss; there is no invalidation
logic to keep in sync, because the key already reflects whatever changed.
"""
import hashlib
import json
import logging
from typing import AsyncIterator, Optional

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.groq_client import safe_groq_stream

logger = logging.getLogger(__name__)

# Separate connection pool from limiter.py's — same justification (a new TCP
# connection per call doesn't scale), kept local rather than importing
# limiter's private `_redis` so this module has no reason to know about
# rate-limiting internals.
_redis = aioredis.from_url(settings.redis_url, max_connections=20)

# Long-lived on purpose: the underlying data never changes on its own, so a
# cached reading never goes stale by itself. CACHE_VERSION exists for the
# one thing that *can* invalidate it — a prompt wording change — without
# needing per-key bookkeeping: bump it and every key changes at once.
CACHE_TTL = 60 * 60 * 24 * 90  # 90 days
CACHE_VERSION = 1


def interpretation_cache_key(*parts: str) -> str:
    """`parts` should be the exact deterministic inputs to the prompt (not
    the owning user/child/partner id) — see module docstring."""
    return "interpret:v{}:{}".format(CACHE_VERSION, ":".join(parts))


def name_fingerprint(name: Optional[str]) -> str:
    """A stable, bounded-length key component for free-text inputs (e.g. a
    numerology full name) that shouldn't go into a Redis key raw."""
    if not name:
        return "none"
    return hashlib.md5(name.strip().lower().encode("utf-8")).hexdigest()[:16]


async def peek_cached_interpretation(cache_key: str) -> Optional[str]:
    """Cheap pre-check so a caller can skip rate-limit/in-flight checks
    entirely on a cache hit — those exist to protect the LLM, and a cache
    hit never touches it."""
    try:
        cached = await _redis.get(cache_key)
    except Exception as e:
        logger.warning("Interpretation cache read failed (falling back to live): %s", e)
        return None
    if cached is None:
        return None
    return cached.decode("utf-8") if isinstance(cached, bytes) else cached


async def cached_groq_stream(
    cache_key: str,
    messages: list[dict],
    max_tokens: int = 900,
    lang: str = "ru",
) -> AsyncIterator[str]:
    """Same SSE shape as safe_groq_stream() — a cache hit is indistinguishable
    to the client from a live stream, just faster. On a miss, taps the live
    stream to accumulate the full text and writes it to cache only if the
    generation actually completed cleanly (finish_reason == "stop", no
    error event) — a truncated or failed generation must never be cached."""
    cached = await peek_cached_interpretation(cache_key)
    if cached is not None:
        yield f"data: {json.dumps({'text': cached})}\n\n"
        yield "data: [DONE]\n\n"
        return

    chunks: list[str] = []
    saw_error = False
    finish_reason: Optional[str] = None

    def _capture_finish(reason: Optional[str]) -> None:
        nonlocal finish_reason
        finish_reason = reason

    async for line in safe_groq_stream(messages, max_tokens=max_tokens, lang=lang, on_finish=_capture_finish):
        yield line
        if not line.startswith("data: "):
            continue
        payload = line[len("data: "):].strip()
        if payload == "[DONE]":
            continue
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if "error" in parsed:
            saw_error = True
        elif "text" in parsed:
            chunks.append(parsed["text"])

    if saw_error or finish_reason != "stop" or not chunks:
        return

    try:
        await _redis.setex(cache_key, CACHE_TTL, "".join(chunks))
    except Exception as e:
        logger.warning("Interpretation cache write failed: %s", e)
