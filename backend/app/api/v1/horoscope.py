import json
import os
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

TONES = {
    "ru": "мягко, образно, с душой, на русском языке",
    "en": "empowering, wellness-focused, in English",
}

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
    tone = TONES.get(req.lang, TONES["ru"])
    today = date.today().isoformat()
    cache_key = f"horoscope:{req.sign}:{req.lang}:{today}"

    prompt = (
        f"Напиши персональный гороскоп для знака {sign_name} "
        f"на {req.date or 'сегодня'}. "
        f"Тон: {tone}. "
        f"Объём: 60-80 слов. "
        f"Без вступлений, без 'Дорогой знак', сразу по делу. "
        f"Без дисклеймеров."
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
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=200,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_text += delta
                yield f"data: {json.dumps({'text': delta})}\n\n"

        await redis_client.set(cache_key, full_text, ex=86400)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
