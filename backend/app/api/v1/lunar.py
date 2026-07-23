import json
import os
from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import lang_enforce as get_lang_enforce, system_prompt
from app.core.structural_i18n import localized_field, pick, pick_list
from app.data.lunar_days import LUNAR_DAYS
from app.data.lunar_i18n import EVENT_DATA_I18N, LUNAR_DAYS_I18N, MOON_SIGNS_I18N, PHASE_NAMES_I18N
from app.data.moon_signs import MOON_SIGNS
# Reused rather than duplicated: SIGNS/SIGNS_RU below are the same 12 zodiac
# names natal.py already has translations for (natal_i18n.SIGNS_I18N).
from app.data.natal_i18n import SIGNS_I18N as ZODIAC_SIGNS_I18N
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


# TZ-080: every field below used to be a plain `RU if ru else EN` ternary,
# which silently collapsed ES/PT/TR/UK to English. These route through the
# i18n modules so those four languages get real content once generated,
# with English as the fallback until then.
def _sign_name(idx: int, lang: str) -> str:
    if lang == "ru":
        return SIGNS_RU[idx]
    sign = SIGNS[idx]
    return sign if lang == "en" else localized_field(ZODIAC_SIGNS_I18N, lang, sign, "name", sign)


def _phase_name(idx: int, lang: str) -> str:
    if lang == "ru":
        return PHASE_NAMES_RU[idx]
    en_value = PHASE_NAMES_EN[idx]
    return en_value if lang == "en" else localized_field(PHASE_NAMES_I18N, lang, str(idx), "name", en_value)


def _event_field(event: dict, field: str, key: str, lang: str) -> str:
    return pick(event, field, lang, EVENT_DATA_I18N, key)


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


def get_upcoming_events(days: int = 14, lang: str = "ru", from_dt: Optional[datetime] = None) -> list[dict]:
    now = from_dt or datetime.utcnow()
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
                    "title": _event_field(ed, "title", event_type, lang) if ed else "",
                    "description": _event_field(ed, "desc", event_type, lang) if ed else "",
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
                                "icon": ed["icon"], "title": _event_field(ed, "title", "mercury_direct", lang),
                                "description": _event_field(ed, "desc", "mercury_direct", lang), "days_until": day_offset + 1})
                break
            if not m1_retro and m2_retro:
                ed = EVENT_DATA["mercury_retro"]
                events.append({"type": "mercury_retro", "date": dt2.strftime("%Y-%m-%d"),
                                "icon": ed["icon"], "title": _event_field(ed, "title", "mercury_retro", lang),
                                "description": _event_field(ed, "desc", "mercury_retro", lang), "days_until": day_offset + 1})
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


def _day_field(day_data: dict, field: str, day_key: int, lang: str) -> str:
    return pick(day_data, field, lang, LUNAR_DAYS_I18N, str(day_key))


def _day_list(day_data: dict, field: str, day_key: int, lang: str) -> list[str]:
    return pick_list(day_data, field, lang, LUNAR_DAYS_I18N, str(day_key))


def _sign_field(sign_data: dict, field: str, sign_key: str, lang: str) -> str:
    return pick(sign_data, field, lang, MOON_SIGNS_I18N, sign_key) if sign_data else ""


def _sign_list(sign_data: dict, field: str, sign_key: str, lang: str) -> list[str]:
    return pick_list(sign_data, field, lang, MOON_SIGNS_I18N, sign_key) if sign_data else []


def get_lunar_today_data(lang: str = "ru", target_date: Optional[date] = None) -> dict:
    dt = datetime(target_date.year, target_date.month, target_date.day, 12, 0) if target_date else datetime.utcnow()
    info = _calc_lunar(dt)
    pi = info["phase_index"]
    si = info["sign_index"]
    ld = min(info["lunar_day"], 30)

    day_data = LUNAR_DAYS.get(ld, LUNAR_DAYS[1])
    sign_key = SIGNS[si]
    sign_data = MOON_SIGNS.get(sign_key, {})

    return {
        "lunar_day": ld,
        "phase_name": _phase_name(pi, lang),
        "phase_icon": PHASE_ICONS[pi],
        "moon_sign": _sign_name(si, lang),
        "moon_sign_key": sign_key,
        "illumination": info["illumination"],
        "energy": day_data.get("energy", "neutral"),
        "day_symbol": _day_field(day_data, "symbol", ld, lang),
        "day_title": _day_field(day_data, "title", ld, lang),
        "day_desc": _day_field(day_data, "desc", ld, lang),
        "favorable": _day_list(day_data, "favorable", ld, lang),
        "unfavorable": _day_list(day_data, "unfavorable", ld, lang),
        "health": _day_field(day_data, "health", ld, lang),
        "beauty": _day_field(day_data, "beauty", ld, lang),
        "money": _day_field(day_data, "money", ld, lang),
        "love": _day_field(day_data, "love", ld, lang),
        "work": _day_field(day_data, "work", ld, lang),
        "spiritual": _day_field(day_data, "spiritual", ld, lang),
        "dreams": _day_field(day_data, "dreams", ld, lang),
        "stones": _day_field(day_data, "stones", ld, lang),
        "sign_desc": _sign_field(sign_data, "desc", sign_key, lang),
        "sign_favorable": _sign_list(sign_data, "favorable", sign_key, lang),
        "sign_unfavorable": _sign_list(sign_data, "unfavorable", sign_key, lang),
        "sign_beauty": _sign_field(sign_data, "beauty", sign_key, lang),
        "sign_health": _sign_field(sign_data, "health", sign_key, lang),
        "upcoming_events": get_upcoming_events(14, lang, dt),
    }


VALID_LANGS = {"ru", "en", "es", "pt", "tr", "uk"}


@router.get("/lunar/today")
async def lunar_today(lang: str = "ru", date: Optional[str] = None):
    if lang not in VALID_LANGS:
        lang = "en"
    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(400, "Invalid date format, expected YYYY-MM-DD")
    # get_upcoming_events runs up to ~60 kerykeion chart builds — cache aggressively
    import redis.asyncio as aioredis
    # explicit date: result never changes, cache long. No date ("today"): cache per hour.
    cache_key = f"lunar_today:{lang}:{date}" if date else f"lunar_today:{lang}:{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
    ttl = 86400 if date else 3900
    r = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    try:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)
        data = get_lunar_today_data(lang, target_date)
        await r.setex(cache_key, ttl, json.dumps(data, ensure_ascii=False))
        return data
    except Exception:
        return get_lunar_today_data(lang, target_date)
    finally:
        await r.close()


@router.get("/lunar/month")
async def lunar_month(lang: str = "ru", year: Optional[int] = None, month: Optional[int] = None):
    today = date.today()
    y = year or today.year
    m = month or today.month
    if not (1 <= m <= 12):
        raise HTTPException(400, "Invalid month, expected 1-12")
    _, days_in_month = monthrange(y, m)
    result = []
    for d in range(1, days_in_month + 1):
        dt = datetime(y, m, d, 12, 0)
        info = _calc_lunar(dt)
        ld = min(info["lunar_day"], 30)
        day_data = LUNAR_DAYS.get(ld, LUNAR_DAYS[1])
        result.append({
            "date": f"{y}-{m:02d}-{d:02d}",
            "lunar_day": ld,
            "phase_icon": PHASE_ICONS[info["phase_index"]],
            "moon_sign": _sign_name(info["sign_index"], lang),
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
    session: AsyncSession = Depends(get_session),
):
    # get_current_user pulls a pooled connection via its own Depends(get_session);
    # release it now instead of holding it for the whole SSE stream below.
    await session.close()
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    data = get_lunar_today_data(req.lang)
    question_part = f'\nВопрос: "{req.question}". Ответь конкретно.' if req.question else ""

    if req.lang == "ru":
        prompt = (
            f"{data['lunar_day']}-й лунный день «{data['day_symbol']}» — {data['day_title']}.\n"
            f"Фаза: {data['phase_name']}. Луна в {data['moon_sign']}.\n"
            f"Энергия дня: {data['energy']}.\n"
            f"Дай рекомендацию на сегодня: что делать и чего избегать. "
            f"Учитывай лунный день, знак Луны и фазу. Только практика.{question_part}\n"
            f"Называй конкретные ситуации и действия. 150-250 слов, без воды."
        )
    else:
        question_en = f'\nQuestion: "{req.question}". Answer specifically.' if req.question else ""
        prompt = (
            f"Lunar day {data['lunar_day']} «{data['day_symbol']}» — {data['day_title']}.\n"
            f"Phase: {data['phase_name']}. Moon in {data['moon_sign']}.\n"
            f"Day energy: {data['energy']}.\n"
            f"Give a recommendation for today: what to do and what to avoid. "
            f"Consider lunar day, moon sign and phase. Practice only.{question_en}\n"
            f"Name concrete situations and actions. 150-250 words, no filler."
        )
    prompt += get_lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "lunar_ai", 10, 10)
    sys = system_prompt(req.lang) + get_lang_enforce(req.lang)
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=700, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
