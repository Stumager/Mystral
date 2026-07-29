import asyncio
import hashlib
import json
import logging
import os
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.prompts import lang_enforce, system_prompt
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Was 700 — tight for a "three paragraphs, 150-250 words" prompt once you
# account for less token-efficient output languages (diacritics/agglutination
# fragment into more subword tokens) and the model's documented tendency to
# ramble before committing (same lesson already learned for SEO/offline-
# horoscope generation, see those modules). A generous ceiling costs nothing
# on responses that finish well under it.
GENERATION_MAX_TOKENS = 1400

# TZ-107: 1-2 sentences at ~DIGEST_MAX_CHARS target — small, but not cut so
# tight that a less token-efficient output language (diacritics/agglutination
# fragmenting into more subword tokens, same lesson as GENERATION_MAX_TOKENS
# above) clips mid-sentence and gets skip-cached.
DIGEST_GENERATION_MAX_TOKENS = 300
# ~2-3 short sentences in this app's house style — enough to feel like a real
# teaser, short enough that the CTA button ("Открыть Mystral") still has a
# reason to exist rather than the push already containing the whole thing.
DIGEST_MAX_CHARS = 240

VALID_SIGNS = {"aries", "taurus", "gemini", "cancer", "leo", "virgo",
               "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"}
VALID_LANGS = {"ru", "en", "es", "pt", "tr", "uk"}

# TZ-107: the old check-cache/generate/set-cache sequence in the functions
# below had a gap between the cache-miss check and the cache write — two
# callers landing in that gap at the same moment (e.g. the scheduler's daily
# push and a live app request for the same sign+lang+day, both reading an
# empty cache) each ran their own independent LLM completion and could each
# show a *different* result before either write landed. This was the
# confirmed mechanism behind a report of the broadcast showing "Sun-Venus"
# while the app showed "Sun-Mars" for the same sign on the same day: not a
# stale value surviving from an old deploy, two live generations racing.
# A short NX lock — same primitive as limiter.check_not_in_flight — makes
# the second caller wait for the first's result instead of generating its
# own; this only ever matters once per sign+lang+day, at whichever request
# happens to be first (every later reader that day is a cache hit already).
_LOCK_TTL = 60
_LOCK_POLL_INTERVAL = 0.5


async def _acquire_lock(cache_key: str) -> bool:
    return bool(await redis_client.set(f"lock:{cache_key}", "1", ex=_LOCK_TTL, nx=True))


async def _release_lock(cache_key: str) -> None:
    await redis_client.delete(f"lock:{cache_key}")


async def _wait_for_peer_result(cache_key: str) -> str | None:
    """Poll while another caller holds the generation lock for this key."""
    elapsed = 0.0
    while elapsed < _LOCK_TTL:
        await asyncio.sleep(_LOCK_POLL_INTERVAL)
        elapsed += _LOCK_POLL_INTERVAL
        cached = await redis_client.get(cache_key)
        if cached:
            return cached.decode()
        if not await redis_client.exists(f"lock:{cache_key}"):
            return None  # holder released without writing a result — give up waiting
    return None

SIGNS_RU = {
    "aries": "Овен",
    "taurus": "Телец",
    "gemini": "Близнецы",
    "cancer": "Рак",
    "leo": "Лев",
    "virgo": "Дева",
    "libra": "Весы",
    "scorpio": "Скорпион",
    "sagittarius": "Стрелец",
    "capricorn": "Козерог",
    "aquarius": "Водолей",
    "pisces": "Рыбы",
}

SIGNS_I18N = {
    "es": {"aries": "Aries", "taurus": "Tauro", "gemini": "Géminis", "cancer": "Cáncer", "leo": "Leo", "virgo": "Virgo", "libra": "Libra", "scorpio": "Escorpio", "sagittarius": "Sagitario", "capricorn": "Capricornio", "aquarius": "Acuario", "pisces": "Piscis"},
    "pt": {"aries": "Áries", "taurus": "Touro", "gemini": "Gêmeos", "cancer": "Câncer", "leo": "Leão", "virgo": "Virgem", "libra": "Libra", "scorpio": "Escorpião", "sagittarius": "Sagitário", "capricorn": "Capricórnio", "aquarius": "Aquário", "pisces": "Peixes"},
    "tr": {"aries": "Koç", "taurus": "Boğa", "gemini": "İkizler", "cancer": "Yengeç", "leo": "Aslan", "virgo": "Başak", "libra": "Terazi", "scorpio": "Akrep", "sagittarius": "Yay", "capricorn": "Oğlak", "aquarius": "Kova", "pisces": "Balık"},
    "uk": {"aries": "Овен", "taurus": "Телець", "gemini": "Близнюки", "cancer": "Рак", "leo": "Лев", "virgo": "Діва", "libra": "Терези", "scorpio": "Скорпіон", "sagittarius": "Стрілець", "capricorn": "Козеріг", "aquarius": "Водолій", "pisces": "Риби"},
}


def _sign_name(sign: str, lang: str) -> str:
    if lang == "ru":
        return SIGNS_RU.get(sign, sign)
    if lang in SIGNS_I18N:
        return SIGNS_I18N[lang].get(sign, sign.capitalize())
    return sign.capitalize()


class HoroscopeRequest(BaseModel):
    sign: str
    lang: str = "ru"
    date: str = ""


# TZ-104: the ONE prompt for "today's horoscope for this sign+lang" — used by
# the interactive endpoint below AND by the scheduler's daily Telegram digest
# (get_cached_or_generate_horoscope). Before this ticket, the scheduler had
# its own separate generation (app/services/horoscope.py's generate_horoscope,
# now removed) with its own prompt that enumerated life areas in a fixed,
# never-randomized order ("работа/отношения/финансы/здоровье" — "work" always
# listed first) — which is why the daily push converged on "work" as the
# featured life area on almost every date for almost every sign, and diverged
# from what the app itself showed for the same sign+lang+day. This prompt has
# no such enumeration (it asks for "energy of the day" broadly, not a pick
# from a fixed menu), so unifying the two call sites onto it removes the
# anchoring mechanism rather than trying to re-balance the old one.
def build_daily_prompt(sign: str, lang: str, target_date: str) -> tuple[str, str]:
    sname = _sign_name(sign, lang)
    sys = system_prompt(lang) + lang_enforce(lang)

    if lang == "ru":
        prompt = (
            f"Составь персональный гороскоп для знака {sname} на {target_date}.\n"
            f"Структура ответа — три чётких абзаца:\n"
            f"1. Энергетика дня — планетарные влияния, конкретные аспекты\n"
            f"2. Практика — что делать и чего избегать, с конкретным временем если уместно\n"
            f"3. Итог — одна ёмкая практическая рекомендация\n"
            f"Без философии и лирики. Называй конкретные ситуации и время. "
            f"150-250 слов, без воды. Без вступлений типа 'Дорогой {sname}'."
        )
    else:
        prompt = (
            f"Write a personal horoscope for {sname} on {target_date}.\n"
            f"Response structure — three clear paragraphs:\n"
            f"1. Energy of the day — planetary influences, specific aspects\n"
            f"2. Practice — what to do and avoid, with specific timing if relevant\n"
            f"3. Takeaway — one concise practical recommendation\n"
            f"No philosophy, no lyricism. Name concrete situations and times. "
            f"150-250 words, no filler. No greetings like 'Dear {sname}'."
        )
    prompt += lang_enforce(lang)
    return sys, prompt


async def get_cached_or_generate_horoscope(sign: str, lang: str) -> str:
    """Plain (non-streaming) cache-or-generate, for the scheduler's daily
    push (TZ-104) — the interactive endpoint below has its own SSE variant of
    this same cache-then-generate logic, for progressive rendering.

    Guarantees the push can never go out before today's horoscope for this
    sign+lang exists in the cache: on a miss, this call generates and caches
    it right here before returning, rather than assuming some app user's own
    request will have populated it first. TZ-107: also lock-guarded (see
    _acquire_lock above) so a concurrent caller for the same key waits for
    this result instead of generating its own.
    """
    today = date.today().isoformat()
    cache_key = f"horoscope:{sign}:{lang}:{today}"
    cached = await redis_client.get(cache_key)
    if cached:
        return cached.decode()

    acquired = await _acquire_lock(cache_key)
    if not acquired:
        waited = await _wait_for_peer_result(cache_key)
        if waited:
            return waited
        acquired = await _acquire_lock(cache_key)

    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return cached.decode()

        sys, prompt = build_daily_prompt(sign, lang, today)
        full_text = ""
        truncated = False

        def _on_finish(reason):
            nonlocal truncated
            truncated = reason == "length"

        msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]
        async for chunk_data in safe_groq_stream(msgs, max_tokens=GENERATION_MAX_TOKENS, lang=lang, on_finish=_on_finish):
            if chunk_data.startswith("data: {"):
                try:
                    parsed = json.loads(chunk_data[6:].strip())
                    if "text" in parsed:
                        full_text += parsed["text"]
                except Exception:
                    pass

        if full_text and not truncated:
            await redis_client.set(cache_key, full_text, ex=86400)
        elif full_text:
            logger.warning("Horoscope %s/%s truncated mid-generation (digest path), not caching", sign, lang)
        return full_text
    finally:
        if acquired:
            await _release_lock(cache_key)


def build_digest_prompt(sign: str, lang: str, full_text: str) -> tuple[str, str]:
    sname = _sign_name(sign, lang)
    sys = system_prompt(lang) + lang_enforce(lang)
    if lang == "ru":
        prompt = (
            f"Вот полный гороскоп дня для {sname}:\n\n{full_text}\n\n"
            f"Перескажи его в 1-2 предложениях (примерно {DIGEST_MAX_CHARS} символов) "
            f"для push-уведомления. Сохрани главную мысль и тон, не обрывай мысль "
            f"на середине. Без вступлений вроде 'Дорогой {sname}' — сразу суть."
        )
    else:
        prompt = (
            f"Here is today's full horoscope for {sname}:\n\n{full_text}\n\n"
            f"Paraphrase it in 1-2 sentences (about {DIGEST_MAX_CHARS} characters) "
            f"for a push notification. Keep the main point and tone, don't cut the "
            f"thought off mid-way. No greeting like 'Dear {sname}' — straight to the point."
        )
    prompt += lang_enforce(lang)
    return sys, prompt


async def get_cached_or_generate_digest(sign: str, lang: str) -> str:
    """TZ-107: the push used to build its teaser by mechanically truncating
    the full horoscope's raw text (see scheduler._build_digest) — even with
    the sentence-boundary guard that added, a cut is still a cut, not a
    summary. This asks the model for an actual short paraphrase instead,
    generated once per sign+lang+day (never per user, same cost profile as
    the main horoscope) and cached the same way. Returns "" on failure —
    callers should fall back to scheduler._build_digest(full_text) rather
    than block delivery on this succeeding.
    """
    today = date.today().isoformat()
    cache_key = f"horoscope_digest:{sign}:{lang}:{today}"
    cached = await redis_client.get(cache_key)
    if cached:
        return cached.decode()

    full_text = await get_cached_or_generate_horoscope(sign, lang)
    if not full_text:
        return ""

    acquired = await _acquire_lock(cache_key)
    if not acquired:
        waited = await _wait_for_peer_result(cache_key)
        if waited:
            return waited
        acquired = await _acquire_lock(cache_key)

    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return cached.decode()

        sys, prompt = build_digest_prompt(sign, lang, full_text)
        digest_text = ""
        truncated = False

        def _on_finish(reason):
            nonlocal truncated
            truncated = reason == "length"

        msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]
        async for chunk_data in safe_groq_stream(msgs, max_tokens=DIGEST_GENERATION_MAX_TOKENS, lang=lang, on_finish=_on_finish):
            if chunk_data.startswith("data: {"):
                try:
                    parsed = json.loads(chunk_data[6:].strip())
                    if "text" in parsed:
                        digest_text += parsed["text"]
                except Exception:
                    pass

        digest_text = digest_text.strip()
        if digest_text and not truncated:
            await redis_client.set(cache_key, digest_text, ex=86400)
            return digest_text
        if digest_text:
            logger.warning("Digest %s/%s truncated mid-generation, not caching", sign, lang)
        return ""
    finally:
        if acquired:
            await _release_lock(cache_key)


@router.post("/horoscope/stream")
async def horoscope_stream(
    req: HoroscopeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # get_current_user pulls a pooled connection via its own Depends(get_session);
    # release it now instead of holding it for the whole SSE stream below.
    await session.close()
    # Whitelist both params: they form the Redis cache key and each unique
    # combination triggers a fresh (paid) Groq generation.
    if req.sign not in VALID_SIGNS:
        raise HTTPException(status_code=422, detail="Invalid sign")
    if req.lang not in VALID_LANGS:
        req.lang = "en"

    today = date.today().isoformat()
    cache_key = f"horoscope:{req.sign}:{req.lang}:{today}"
    sys, prompt = build_daily_prompt(req.sign, req.lang, req.date or today)

    async def _stream_cached(text: str):
        for char in text:
            yield f"data: {json.dumps({'text': char})}\n\n"
        yield "data: [DONE]\n\n"

    async def generate():
        cached = await redis_client.get(cache_key)
        if cached:
            async for line in _stream_cached(cached.decode()):
                yield line
            return

        # TZ-107: another request for this exact sign+lang+day (e.g. the
        # scheduler's pre-warm, or another viewer) may already be generating
        # — wait for its result instead of also calling the LLM, so the two
        # can't diverge (see _acquire_lock's docstring above).
        acquired = await _acquire_lock(cache_key)
        if not acquired:
            waited = await _wait_for_peer_result(cache_key)
            if waited:
                async for line in _stream_cached(waited):
                    yield line
                return
            acquired = await _acquire_lock(cache_key)

        try:
            cached = await redis_client.get(cache_key)
            if cached:
                async for line in _stream_cached(cached.decode()):
                    yield line
                return

            full_text = ""
            truncated = False

            def _on_finish(reason):
                nonlocal truncated
                truncated = reason == "length"

            msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]
            async for chunk_data in safe_groq_stream(msgs, max_tokens=GENERATION_MAX_TOKENS, lang=req.lang, on_finish=_on_finish):
                yield chunk_data
                if chunk_data.startswith("data: {"):
                    try:
                        parsed = json.loads(chunk_data[6:].strip())
                        if "text" in parsed:
                            full_text += parsed["text"]
                    except Exception:
                        pass

            if full_text and truncated:
                # Don't cache a cut-off result — it would otherwise serve the
                # same broken text to every viewer of this sign/lang/day for the
                # full 24h TTL instead of letting the next request try again.
                logger.warning("Horoscope %s/%s truncated mid-generation, not caching", req.sign, req.lang)
            elif full_text:
                await redis_client.set(cache_key, full_text, ex=86400)
        finally:
            if acquired:
                await _release_lock(cache_key)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/horoscope/scores")
async def horoscope_scores(sign: str = "aries", date: str = ""):
    if sign not in VALID_SIGNS:
        raise HTTPException(status_code=422, detail="Invalid sign")
    today = date or __import__("datetime").date.today().isoformat()
    cache_key = f"scores:{sign}:{today}"

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    h = hashlib.md5(f"{sign}{today}".encode()).hexdigest()
    love = 55 + int(h[0:2], 16) % 41
    career = 55 + int(h[2:4], 16) % 41
    health = 55 + int(h[4:6], 16) % 41

    result = {"love": love, "career": career, "health": health}
    await redis_client.set(cache_key, json.dumps(result), ex=86400)
    return result
