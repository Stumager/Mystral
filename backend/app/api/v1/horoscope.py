import json
import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

    prompt = (
        f"Напиши персональный гороскоп для знака {sign_name} "
        f"на {req.date or 'сегодня'}. "
        f"Тон: {tone}. "
        f"Объём: 60-80 слов. "
        f"Без вступлений, без 'Дорогой знак', сразу по делу. "
        f"Без дисклеймеров."
    )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=200,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'text': delta})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
