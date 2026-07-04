import json
import os
from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import lang_enforce as get_lang_enforce, system_prompt
from app.data.lunar_days import LUNAR_DAYS
from app.data.moon_signs import MOON_SIGNS
from app.models.user import User

router = APIRouter()

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


EVENT_DATA = {
    "new_moon":       {"icon": "🌑", "title_ru": "Новолуние",         "title_en": "New Moon",
                       "desc_ru": "Начало нового цикла. Идеально для постановки целей и намерений.",
                       "desc_en": "Start of a new cycle. Perfect for setting goals and intentions."},
    "first_quarter":  {"icon": "🌓", "title_ru": "Первая четверть",   "title_en": "First Quarter",
                       "desc_ru": "Время действий. Преодолевай препятствия, двигайся к целям.",
                       "desc_en": "Time for action. Overcome obstacles, move toward goals."},
    "full_moon":      {"icon": "🌕", "title_ru": "Полнолуние",        "title_en": "Full Moon",
                       "desc_ru": "Кульминация цикла. Эмоции на пике. Завершай дела, празднуй результаты.",
                       "desc_en": "Cycle culmination. Emotions peak. Finish tasks, celebrate results."},
    "last_quarter":   {"icon": "🌗", "title_ru": "Последняя четверть", "title_en": "Last Quarter",
                       "desc_ru": "Отпускай и очищай. Время для ревизии и избавления от лишнего.",
                       "desc_en": "Let go and cleanse. Time for review and releasing the unnecessary."},
    "mercury_retro":  {"icon": "☿️↩", "title_ru": "Меркурий ретроград", "title_en": "Mercury Retrograde",
                       "desc_ru": "Задержки в коммуникациях, сбои техники. Перепроверяй всё дважды.",
                       "desc_en": "Communication delays, tech glitches. Double-check everything."},
    "mercury_direct": {"icon": "☿️→", "title_ru": "Меркурий директный", "title_en": "Mercury Direct",
                       "desc_ru": "Коммуникации восстанавливаются. Можно подписывать договоры.",
                       "desc_en": "Communications restored. Safe to sign contracts."},
}


def get_upcoming_events(days: int = 14, lang: str = "ru") -> list[dict]:
    now = datetime.utcnow()
    ru = lang == "ru"
    events = []

    days_since_ref = (now - NEW_MOON_REF).total_seconds() / 86400
    current_cycle_start = days_since_ref - (days_since_ref % LUNAR_CYCLE)

    for phase_offset, event_type in [(0, "new_moon"), (LUNAR_CYCLE * 0.25, "first_quarter"),
                                      (LUNAR_CYCLE * 0.5, "full_moon"), (LUNAR_CYCLE * 0.75, "last_quarter")]:
        for cycle_shift in [0, 1, -1]:
            cycle_base = current_cycle_start + cycle_shift * LUNAR_CYCLE
            event_days = cycle_base + phase_offset
            event_dt = NEW_MOON_REF + timedelta(days=event_days)
            diff = (event_dt - now).total_seconds() / 86400
            if 0 <= diff <= days:
                ed = EVENT_DATA.get(event_type, {})
                events.append({
                    "type": event_type,
                    "date": event_dt.strftime("%Y-%m-%d"),
                    "icon": ed.get("icon", ""),
                    "title": ed.get("title_ru" if ru else "title_en", ""),
                    "description": ed.get("desc_ru" if ru else "desc_en", ""),
                    "days_until": round(diff),
                })

    try:
        from kerykeion import AstrologicalSubject
        for day_offset in range(0, min(days, 30)):
            dt = now + timedelta(days=day_offset)
            dt2 = dt + timedelta(days=1)
            s1 = AstrologicalSubject("t1", dt.year, dt.month, dt.day, 12, 0, lng=0, lat=0, tz_str="UTC", online=False)
            s2 = AstrologicalSubject("t2", dt2.year, dt2.month, dt2.day, 12, 0, lng=0, lat=0, tz_str="UTC", online=False)
            m1_retro = getattr(getattr(s1, "mercury", None), "retrograde", False)
            m2_retro = getattr(getattr(s2, "mercury", None), "retrograde", False)
            if m1_retro and not m2_retro:
                ed = EVENT_DATA["mercury_direct"]
                events.append({"type": "mercury_direct", "date": dt2.strftime("%Y-%m-%d"),
                                "icon": ed["icon"], "title": ed.get("title_ru" if ru else "title_en", ""),
                                "description": ed.get("desc_ru" if ru else "desc_en", ""), "days_until": day_offset + 1})
                break
            if not m1_retro and m2_retro:
                ed = EVENT_DATA["mercury_retro"]
                events.append({"type": "mercury_retro", "date": dt2.strftime("%Y-%m-%d"),
                                "icon": ed["icon"], "title": ed.get("title_ru" if ru else "title_en", ""),
                                "description": ed.get("desc_ru" if ru else "desc_en", ""), "days_until": day_offset + 1})
                break
    except Exception:
        pass

    seen = set()
    unique = []
    for e in sorted(events, key=lambda x: x["days_until"]):
        key = f"{e['type']}:{e['date']}"
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


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
        "upcoming_events": get_upcoming_events(14, lang),
    }


VALID_LANGS = {"ru", "en", "es", "pt", "tr", "uk"}


@router.get("/lunar/today")
async def lunar_today(lang: str = "ru"):
    if lang not in VALID_LANGS:
        lang = "en"
    # get_upcoming_events runs up to ~60 kerykeion chart builds — cache aggressively
    import redis.asyncio as aioredis
    cache_key = f"lunar_today:{lang}:{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
    r = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    try:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)
        data = get_lunar_today_data(lang)
        await r.setex(cache_key, 3900, json.dumps(data, ensure_ascii=False))
        return data
    except Exception:
        return get_lunar_today_data(lang)
    finally:
        await r.close()


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

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "lunar_ai", 10, 10)
    sys = system_prompt(req.lang) + get_lang_enforce(req.lang)
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=350, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
