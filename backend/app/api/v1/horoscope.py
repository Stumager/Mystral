import json
import os
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

from app.core.prompts import system_prompt

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": prompt},
            ],
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
