import hashlib
import json
import os
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.groq_client import safe_groq_stream
from app.core.prompts import system_prompt

router = APIRouter()
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

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


class HoroscopeRequest(BaseModel):
    sign: str
    lang: str = "ru"
    date: str = ""


@router.post("/horoscope/stream")
async def horoscope_stream(req: HoroscopeRequest):
    sign_name = SIGNS_RU.get(req.sign, req.sign)
    today = date.today().isoformat()
    cache_key = f"horoscope:{req.sign}:{req.lang}:{today}"
    sys = system_prompt(req.lang)

    if req.lang == "ru":
        prompt = (
            f"Знак: {sign_name}. Дата: {req.date or today}.\n"
            f"Напиши гороскоп на день. Обязательно укажи:\n"
            f"1. Одну конкретную сферу жизни (работа/отношения/финансы/здоровье)\n"
            f"2. Один конкретный совет что сделать или избежать\n"
            f"3. Благоприятное время дня если уместно\n"
            f"Объём: 60-70 слов. Без вступлений типа 'Дорогой Скорпион'."
        )
    else:
        prompt = (
            f"Sign: {req.sign.capitalize()}. Date: {req.date or today}.\n"
            f"Write a daily horoscope. Must include:\n"
            f"1. One specific life area (work/relationships/finances/health)\n"
            f"2. One concrete tip — what to do or avoid\n"
            f"3. Best time of day if relevant\n"
            f"60-70 words. No greetings like 'Dear Scorpio'."
        )

    async def generate():
        cached = await redis_client.get(cache_key)
        if cached:
            text = cached.decode()
            for char in text:
                yield f"data: {json.dumps({'text': char})}\n\n"
            yield "data: [DONE]\n\n"
            return

        full_text = ""
        msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]
        async for chunk_data in safe_groq_stream(msgs, max_tokens=200, lang=req.lang):
            yield chunk_data
            if chunk_data.startswith("data: {"):
                try:
                    parsed = json.loads(chunk_data[6:].strip())
                    if "text" in parsed:
                        full_text += parsed["text"]
                except Exception:
                    pass

        if full_text:
            await redis_client.set(cache_key, full_text, ex=86400)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/horoscope/scores")
async def horoscope_scores(sign: str = "aries", date: str = ""):
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
