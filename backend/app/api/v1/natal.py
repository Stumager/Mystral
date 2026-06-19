import json
import os

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from kerykeion import AstrologicalSubject
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.prompts import system_prompt
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

SIGNS_RU = {
    "Ari": "Овен",   "Aries": "Овен",
    "Tau": "Телец",  "Taurus": "Телец",
    "Gem": "Близнецы", "Gemini": "Близнецы",
    "Can": "Рак",    "Cancer": "Рак",
    "Leo": "Лев",
    "Vir": "Дева",   "Virgo": "Дева",
    "Lib": "Весы",   "Libra": "Весы",
    "Sco": "Скорпион", "Scorpio": "Скорпион",
    "Sag": "Стрелец", "Sagittarius": "Стрелец",
    "Cap": "Козерог", "Capricorn": "Козерог",
    "Aqu": "Водолей", "Aquarius": "Водолей",
    "Pis": "Рыбы",   "Pisces": "Рыбы",
}


class NatalRequest(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    city: str
    lang: str = "ru"


def _ru(sign: str) -> str:
    return SIGNS_RU.get(sign, SIGNS_RU.get(sign[:3], sign))


async def geocode_city(city: str) -> tuple[float, float]:
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "Mystral/1.0"},
        )
    data = resp.json()
    if not data:
        raise HTTPException(status_code=422, detail=f"Город не найден: {city}")
    return float(data[0]["lat"]), float(data[0]["lon"])


def build_chart(req: NatalRequest, lat: float, lon: float) -> dict:
    subject = AstrologicalSubject(
        req.name, req.year, req.month, req.day,
        req.hour, req.minute,
        lng=lon, lat=lat, tz_str="UTC", online=False,
    )
    return {
        "sun":     {"sign": _ru(subject.sun.sign),     "degree": round(subject.sun.position, 1)},
        "moon":    {"sign": _ru(subject.moon.sign),    "degree": round(subject.moon.position, 1)},
        "rising":  {"sign": _ru(subject.first_house.sign), "degree": round(subject.first_house.position, 1)},
        "mercury": {"sign": _ru(subject.mercury.sign)},
        "venus":   {"sign": _ru(subject.venus.sign)},
        "mars":    {"sign": _ru(subject.mars.sign)},
    }


@router.post("/natal/calculate")
async def natal_calculate(req: NatalRequest):
    lat, lon = await geocode_city(req.city)
    return build_chart(req, lat, lon)


@router.post("/natal/interpret")
async def natal_interpret(
    req: NatalRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier == "free":
        key = f"natal_count:{current_user.id}"
        count = await redis_client.incr(key)
        if count > 3:
            raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    lat, lon = await geocode_city(req.city)
    chart = build_chart(req, lat, lon)

    sys = system_prompt(req.lang)
    sun = chart["sun"]["sign"]
    moon = chart["moon"]["sign"]
    rising = chart["rising"]["sign"]

    if req.lang == "ru":
        prompt = (
            f"Натальная карта: Солнце в {sun}, Луна в {moon}, Асцендент {rising}.\n"
            f"Дай интерпретацию характера человека. Обязательно:\n"
            f"1. Главная черта характера (Солнце) — конкретно\n"
            f"2. Эмоциональная природа (Луна) — конкретно\n"
            f"3. Как человек воспринимается окружающими (Асцендент)\n"
            f"4. Главное противоречие или вызов этого сочетания\n"
            f"Объём: 100-120 слов."
        )
    else:
        prompt = (
            f"Natal chart: Sun in {sun}, Moon in {moon}, Ascendant {rising}.\n"
            f"Interpret this person's character. Must include:\n"
            f"1. Core personality trait (Sun) — be specific\n"
            f"2. Emotional nature (Moon) — be specific\n"
            f"3. How others perceive them (Ascendant)\n"
            f"4. The main tension or challenge of this combination\n"
            f"100-120 words."
        )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=300,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'text': delta})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
