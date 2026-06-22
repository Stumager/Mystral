import json
import os
from datetime import date, datetime

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import system_prompt
from app.data.numerology import (
    ANGEL_NUMBERS,
    KARMIC_DESCRIPTIONS_EN,
    KARMIC_DESCRIPTIONS_RU,
    NUMBER_DATA,
    birthday_number,
    destiny_number,
    get_number_data,
    karmic_numbers,
    life_path,
    missing_numbers,
    personal_day,
    personal_month,
    personal_year,
    personality_number,
    pythagoras_square,
    reduce,
    soul_number,
)
from app.models.user import User, UserProfile

router = APIRouter()
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")


@router.get("/numerology/profile")
async def numerology_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    r = aioredis.from_url(redis_url)
    cache_key = f"numerology:{current_user.id}"
    try:
        cached = await r.get(cache_key)
        if cached:
            await r.close()
            return json.loads(cached)
    except Exception:
        pass

    result_q = await session.exec(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result_q.first()
    if not profile or not profile.birth_date:
        raise HTTPException(400, "birth_date required")

    bd = profile.birth_date
    lang = current_user.lang or "ru"
    ru = lang == "ru"
    today = date.today()
    fn = profile.full_name

    lp = life_path(bd)
    bd_num = birthday_number(bd)
    py = personal_year(bd, today.year)
    pm = personal_month(bd, today.year, today.month)
    pd = personal_day(bd, today)

    result: dict = {
        "life_path": {"number": lp, "is_master": lp in (11, 22, 33), "data": get_number_data(lp, lang)},
        "birthday": {"number": bd_num, "data": get_number_data(bd_num, lang)},
        "personal_year": {"number": py, "year": today.year, "data": get_number_data(py, lang)},
        "personal_month": {"number": pm, "data": get_number_data(pm, lang)},
        "personal_day": {"number": pd, "data": get_number_data(pd, lang)},
        "requires_full_name": not fn,
    }

    if fn:
        dn = destiny_number(fn)
        sn = soul_number(fn)
        pn = personality_number(fn)
        result["destiny"] = {"number": dn, "is_master": dn in (11, 22, 33), "data": get_number_data(dn, lang)}
        result["soul"] = {"number": sn, "is_master": sn in (11, 22, 33), "data": get_number_data(sn, lang)}
        result["personality"] = {"number": pn, "is_master": pn in (11, 22, 33), "data": get_number_data(pn, lang)}
    else:
        result["destiny"] = None
        result["soul"] = None
        result["personality"] = None

    kn = karmic_numbers(bd)
    descs = KARMIC_DESCRIPTIONS_RU if ru else KARMIC_DESCRIPTIONS_EN
    for k in kn:
        k["description"] = descs.get(k["number"], "")
    result["karmic_numbers"] = kn

    mn = missing_numbers(bd)
    result["missing_numbers"] = mn

    result["pythagoras_square"] = pythagoras_square(bd, lang)

    try:
        data_str = json.dumps(result, ensure_ascii=False)
        await r.setex(cache_key, 86400, data_str)
    except Exception:
        pass
    finally:
        await r.close()

    return result


@router.get("/numerology/angel/{number}")
async def angel_number(number: str):
    entry = ANGEL_NUMBERS.get(number)
    if not entry:
        raise HTTPException(404, "Angel number not found")
    return entry


class InterpretRequest(BaseModel):
    section: str
    lang: str = "ru"


@router.post("/numerology/interpret")
async def interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if req.section != "core" and current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    result_q = await session.exec(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result_q.first()
    if not profile or not profile.birth_date:
        raise HTTPException(400, "birth_date required")

    bd = profile.birth_date
    fn = profile.full_name
    ru = req.lang == "ru"
    today = date.today()

    lp = life_path(bd)
    bd_num = birthday_number(bd)

    if req.section == "core":
        name_part = ""
        if fn:
            dn = destiny_number(fn)
            sn = soul_number(fn)
            pn = personality_number(fn)
            if ru:
                name_part = f"\nЧисло Судьбы: {dn}, Число Души: {sn}, Число Личности: {pn}."
            else:
                name_part = f"\nDestiny: {dn}, Soul: {sn}, Personality: {pn}."
        if ru:
            prompt = (
                f"Число Жизненного Пути: {lp}. Число дня рождения: {bd_num}.{name_part}\n"
                f"Дай глубокий нумерологический анализ:\n"
                f"1. Главная жизненная миссия\n"
                f"2. Ключевые сильные стороны\n"
                f"3. Скрытые вызовы и как с ними работать\n"
                f"4. Лучшая сфера для реализации\n"
                f"120-150 слов."
            )
        else:
            prompt = (
                f"Life Path: {lp}. Birthday Number: {bd_num}.{name_part}\n"
                f"Give a deep numerological analysis:\n"
                f"1. Core life mission\n"
                f"2. Key strengths\n"
                f"3. Hidden challenges and how to work with them\n"
                f"4. Best area for fulfillment\n"
                f"120-150 words."
            )

    elif req.section == "square":
        sq = pythagoras_square(bd, req.lang)
        cells_str = ", ".join(f"{c['number']}={c['count']}" for c in sq["cells"])
        strong = [c for c in sq["cells"] if c["count"] >= 3]
        weak = [c for c in sq["cells"] if c["count"] == 0]
        if ru:
            prompt = (
                f"Квадрат Пифагора для даты {bd.isoformat()}:\n"
                f"Ячейки: {cells_str}\n"
                f"Сильные: {', '.join(c['name'] for c in strong) or 'нет'}.\n"
                f"Пустые: {', '.join(c['name'] for c in weak) or 'нет'}.\n"
                f"Дай анализ характера по квадрату. Что является опорой, что нужно развивать. "
                f"Конкретно, без общих фраз. 120-150 слов."
            )
        else:
            prompt = (
                f"Pythagoras Square for {bd.isoformat()}:\n"
                f"Cells: {cells_str}\n"
                f"Strong: {', '.join(c['name'] for c in strong) or 'none'}.\n"
                f"Empty: {', '.join(c['name'] for c in weak) or 'none'}.\n"
                f"Analyze character based on the square. What is the foundation, what needs development. "
                f"Be specific. 120-150 words."
            )

    elif req.section == "forecast":
        py = personal_year(bd, today.year)
        pm = personal_month(bd, today.year, today.month)
        pd = personal_day(bd, today)
        if ru:
            prompt = (
                f"Персональный год: {py}, месяц: {pm}, день: {pd}.\n"
                f"Дай прогноз. Для каждого периода — конкретная рекомендация. "
                f"Что делать сегодня, на что обратить внимание в этом месяце, "
                f"главная тема года. 120-150 слов."
            )
        else:
            prompt = (
                f"Personal year: {py}, month: {pm}, day: {pd}.\n"
                f"Give a forecast. For each period — specific recommendation. "
                f"What to do today, what to focus on this month, "
                f"the main theme of the year. 120-150 words."
            )

    elif req.section == "karmic":
        kn = karmic_numbers(bd)
        mn = missing_numbers(bd)
        if ru:
            kn_str = ", ".join(str(k["number"]) for k in kn) if kn else "нет"
            mn_str = ", ".join(str(m) for m in mn) if mn else "нет"
            prompt = (
                f"Кармические числа: {kn_str}. Отсутствующие числа: {mn_str}.\n"
                f"Объясни кармические уроки и что нужно развивать. "
                f"Конкретные действия для проработки каждого аспекта. 120-150 слов."
            )
        else:
            kn_str = ", ".join(str(k["number"]) for k in kn) if kn else "none"
            mn_str = ", ".join(str(m) for m in mn) if mn else "none"
            prompt = (
                f"Karmic numbers: {kn_str}. Missing numbers: {mn_str}.\n"
                f"Explain karmic lessons and what needs development. "
                f"Specific actions for working through each aspect. 120-150 words."
            )
    else:
        raise HTTPException(400, "Invalid section")

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "numerology_interpret", 2, 20)
    lang_enforce = " Отвечай ТОЛЬКО на русском." if ru else " Answer ONLY in English."
    sys = system_prompt(req.lang) + lang_enforce
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=500, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
