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

VALID_SIGNS = {"aries", "taurus", "gemini", "cancer", "leo", "virgo",
               "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"}
VALID_LANGS = {"ru", "en", "es", "pt", "tr", "uk"}

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

    sname = _sign_name(req.sign, req.lang)
    today = date.today().isoformat()
    cache_key = f"horoscope:{req.sign}:{req.lang}:{today}"
    sys = system_prompt(req.lang) + lang_enforce(req.lang)

    if req.lang == "ru":
        prompt = (
            f"Составь персональный гороскоп для знака {sname} на {req.date or today}.\n"
            f"Структура ответа — три чётких абзаца:\n"
            f"1. Энергетика дня — планетарные влияния, конкретные аспекты\n"
            f"2. Практика — что делать и чего избегать, с конкретным временем если уместно\n"
            f"3. Итог — одна ёмкая практическая рекомендация\n"
            f"Без философии и лирики. Называй конкретные ситуации и время. "
            f"150-250 слов, без воды. Без вступлений типа 'Дорогой {sname}'."
        )
    else:
        prompt = (
            f"Write a personal horoscope for {sname} on {req.date or today}.\n"
            f"Response structure — three clear paragraphs:\n"
            f"1. Energy of the day — planetary influences, specific aspects\n"
            f"2. Practice — what to do and avoid, with specific timing if relevant\n"
            f"3. Takeaway — one concise practical recommendation\n"
            f"No philosophy, no lyricism. Name concrete situations and times. "
            f"150-250 words, no filler. No greetings like 'Dear {sname}'."
        )
    prompt += lang_enforce(req.lang)

    async def generate():
        cached = await redis_client.get(cache_key)
        if cached:
            text = cached.decode()
            for char in text:
                yield f"data: {json.dumps({'text': char})}\n\n"
            yield "data: [DONE]\n\n"
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
