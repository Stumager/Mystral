import json
import os
from calendar import monthrange
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.prompts import system_prompt
from app.data.lunar_days import LUNAR_DAYS
from app.data.moon_signs import MOON_SIGNS
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

NEW_MOON_REF = datetime(2000, 1, 6, 18, 14)
LUNAR_CYCLE = 29.53058867

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
            "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]

PHASE_NAMES_RU = ["Новолуние", "Молодой месяц", "Первая четверть", "Прибывающая",
                  "Полнолуние", "Убывающая", "Последняя четверть", "Старый месяц"]
PHASE_NAMES_EN = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
                  "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
PHASE_ICONS = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]


def _calc_lunar(dt: datetime) -> dict:
    days_since = (dt - NEW_MOON_REF).total_seconds() / 86400
    pos_in_cycle = days_since % LUNAR_CYCLE
    lunar_day = int(pos_in_cycle) + 1
    phase_index = int(pos_in_cycle / LUNAR_CYCLE * 8) % 8
    sign_index = int(pos_in_cycle / LUNAR_CYCLE * 12) % 12
    illumination = round(abs(1 - abs(pos_in_cycle / LUNAR_CYCLE * 2 - 1)) * 100, 1)
    return {
        "lunar_day": min(lunar_day, 30),
        "phase_index": phase_index,
        "sign_index": sign_index,
        "illumination": illumination,
    }


def get_lunar_today_data(lang: str = "ru") -> dict:
    info = _calc_lunar(datetime.utcnow())
    pi = info["phase_index"]
    si = info["sign_index"]
    ld = min(info["lunar_day"], 30)
    ru = lang == "ru"

    day_data = LUNAR_DAYS.get(ld, LUNAR_DAYS[1])
    sign_key = SIGNS[si]
    sign_data = MOON_SIGNS.get(sign_key, {})

    return {
        "lunar_day": ld,
        "phase_name": PHASE_NAMES_RU[pi] if ru else PHASE_NAMES_EN[pi],
        "phase_icon": PHASE_ICONS[pi],
        "moon_sign": SIGNS_RU[si] if ru else SIGNS[si],
        "moon_sign_key": sign_key,
        "illumination": info["illumination"],
        "energy": day_data.get("energy", "neutral"),
        "day_symbol": day_data.get("symbol_ru" if ru else "symbol_en", ""),
        "day_title": day_data.get("title_ru" if ru else "title_en", ""),
        "day_desc": day_data.get("desc_ru" if ru else "desc_en", ""),
        "favorable": day_data.get("favorable_ru" if ru else "favorable_en", []),
        "unfavorable": day_data.get("unfavorable_ru" if ru else "unfavorable_en", []),
        "health": day_data.get("health_ru" if ru else "health_en", ""),
        "beauty": day_data.get("beauty_ru" if ru else "beauty_en", ""),
        "money": day_data.get("money_ru" if ru else "money_en", ""),
        "love": day_data.get("love_ru" if ru else "love_en", ""),
        "work": day_data.get("work_ru" if ru else "work_en", ""),
        "spiritual": day_data.get("spiritual_ru" if ru else "spiritual_en", ""),
        "dreams": day_data.get("dreams_ru" if ru else "dreams_en", ""),
        "stones": day_data.get("stones_ru" if ru else "stones_en", ""),
        "sign_desc": sign_data.get("desc_ru" if ru else "desc_en", ""),
        "sign_favorable": sign_data.get("favorable_ru" if ru else "favorable_en", []),
        "sign_unfavorable": sign_data.get("unfavorable_ru" if ru else "unfavorable_en", []),
        "sign_beauty": sign_data.get("beauty_ru" if ru else "beauty_en", ""),
        "sign_health": sign_data.get("health_ru" if ru else "health_en", ""),
    }


@router.get("/lunar/today")
async def lunar_today(lang: str = "ru"):
    return get_lunar_today_data(lang)


@router.get("/lunar/month")
async def lunar_month(lang: str = "ru"):
    today = date.today()
    _, days_in_month = monthrange(today.year, today.month)
    ru = lang == "ru"
    result = []
    for d in range(1, days_in_month + 1):
        dt = datetime(today.year, today.month, d, 12, 0)
        info = _calc_lunar(dt)
        ld = min(info["lunar_day"], 30)
        day_data = LUNAR_DAYS.get(ld, LUNAR_DAYS[1])
        result.append({
            "date": f"{today.year}-{today.month:02d}-{d:02d}",
            "lunar_day": ld,
            "phase_icon": PHASE_ICONS[info["phase_index"]],
            "moon_sign": SIGNS_RU[info["sign_index"]] if ru else SIGNS[info["sign_index"]],
            "energy": day_data.get("energy", "neutral"),
        })
    return result


class AIRecommendRequest(BaseModel):
    question: Optional[str] = None
    lang: str = "ru"


@router.post("/lunar/ai-recommend")
async def lunar_ai_recommend(
    req: AIRecommendRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    data = get_lunar_today_data(req.lang)
    question_part = f'\nВопрос: "{req.question}". Ответь конкретно.' if req.question else ""

    if req.lang == "ru":
        prompt = (
            f"{data['lunar_day']}-й лунный день «{data['day_symbol']}» — {data['day_title']}.\n"
            f"Фаза: {data['phase_name']}. Луна в {data['moon_sign']}.\n"
            f"Энергия дня: {data['energy']}.\n"
            f"Дай персональную рекомендацию на сегодня. "
            f"Учитывай лунный день, знак Луны и фазу. Конкретно, практично.{question_part}\n"
            f"100-130 слов."
        )
    else:
        question_en = f'\nQuestion: "{req.question}". Answer specifically.' if req.question else ""
        prompt = (
            f"Lunar day {data['lunar_day']} «{data['day_symbol']}» — {data['day_title']}.\n"
            f"Phase: {data['phase_name']}. Moon in {data['moon_sign']}.\n"
            f"Day energy: {data['energy']}.\n"
            f"Give a personal recommendation for today. "
            f"Consider lunar day, moon sign and phase. Be specific and practical.{question_en}\n"
            f"100-130 words."
        )

    lang_enforce = " Отвечай ТОЛЬКО на русском." if req.lang == "ru" else " Answer ONLY in English."
    sys = system_prompt(req.lang) + lang_enforce

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": prompt}],
            stream=True, max_tokens=350,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'text': delta})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
