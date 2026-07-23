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
from app.core.limiter import check_not_in_flight, check_rate_limit, release_in_flight
from app.core.prompts import lang_enforce as get_lang_enforce, system_prompt
from app.core.structural_i18n import localized_field
from app.data.numerology import (
    ANGEL_NUMBERS,
    NUMBER_DATA,
    birthday_number,
    destiny_number,
    get_number_data,
    karmic_description,
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
from app.data.numerology_i18n import ANGEL_NUMBERS_I18N
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
    for k in kn:
        k["description"] = karmic_description(k["number"], lang)
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
async def angel_number(number: str, lang: str = "ru"):
    entry = ANGEL_NUMBERS.get(number)
    if not entry:
        raise HTTPException(404, "Angel number not found")
    # TZ-080: this used to return both meaning_ru/meaning_en unconditionally
    # and let the frontend pick between just those two — ES/PT/TR/UK always
    # got the English meaning. Resolve a single localized field instead.
    if lang == "ru":
        meaning = entry["meaning_ru"]
    else:
        en_value = entry["meaning_en"]
        meaning = en_value if lang == "en" else localized_field(ANGEL_NUMBERS_I18N, lang, number, "meaning", en_value)
    return {**entry, "meaning": meaning}


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

    # QA-035/036: this is the only DB access the request needs. Left open via
    # the Depends(get_session) dependency, it stays checked out of the pool
    # for the entire SSE stream below (13-48s+ observed) — closing it here
    # frees the connection immediately instead of holding it hostage for the
    # LLM call's duration.
    await session.close()

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
                f"Дай нумерологический анализ по схеме число → качества → проявление в реальной жизни:\n"
                f"1. Главная жизненная миссия\n"
                f"2. Ключевые сильные стороны\n"
                f"3. Скрытые вызовы и как с ними работать\n"
                f"4. Лучшая сфера для реализации\n"
                f"Называй конкретные числа, качества и ситуации. 150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Life Path: {lp}. Birthday Number: {bd_num}.{name_part}\n"
                f"Give a numerological analysis following number → qualities → real-life manifestation:\n"
                f"1. Core life mission\n"
                f"2. Key strengths\n"
                f"3. Hidden challenges and how to work with them\n"
                f"4. Best area for fulfillment\n"
                f"Name concrete numbers, traits and situations. 150-250 words, no filler."
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
                f"Дай анализ по схеме число → качество → проявление в реальной жизни. "
                f"Что является опорой, что нужно развивать. Называй конкретные числа и качества. "
                f"150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Pythagoras Square for {bd.isoformat()}:\n"
                f"Cells: {cells_str}\n"
                f"Strong: {', '.join(c['name'] for c in strong) or 'none'}.\n"
                f"Empty: {', '.join(c['name'] for c in weak) or 'none'}.\n"
                f"Give an analysis following number → quality → real-life manifestation. "
                f"What is the foundation, what needs development. Name concrete numbers and traits. "
                f"150-250 words, no filler."
            )

    elif req.section == "forecast":
        py = personal_year(bd, today.year)
        pm = personal_month(bd, today.year, today.month)
        pd = personal_day(bd, today)
        if ru:
            prompt = (
                f"Персональный год: {py}, месяц: {pm}, день: {pd}.\n"
                f"Дай прогноз по схеме число → качество → проявление в реальной жизни для каждого "
                f"периода. Что делать сегодня, на что обратить внимание в этом месяце, "
                f"главная тема года. Называй конкретные числа и ситуации. "
                f"150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Personal year: {py}, month: {pm}, day: {pd}.\n"
                f"Give a forecast following number → quality → real-life manifestation for each "
                f"period. What to do today, what to focus on this month, "
                f"the main theme of the year. Name concrete numbers and situations. "
                f"150-250 words, no filler."
            )

    elif req.section == "karmic":
        kn = karmic_numbers(bd)
        mn = missing_numbers(bd)
        if ru:
            kn_str = ", ".join(str(k["number"]) for k in kn) if kn else "нет"
            mn_str = ", ".join(str(m) for m in mn) if mn else "нет"
            prompt = (
                f"Кармические числа: {kn_str}. Отсутствующие числа: {mn_str}.\n"
                f"Дай анализ по схеме число → урок → конкретное проявление и действия для проработки "
                f"каждого аспекта. 150-250 слов, без воды."
            )
        else:
            kn_str = ", ".join(str(k["number"]) for k in kn) if kn else "none"
            mn_str = ", ".join(str(m) for m in mn) if mn else "none"
            prompt = (
                f"Karmic numbers: {kn_str}. Missing numbers: {mn_str}.\n"
                f"Give an analysis following number → lesson → concrete manifestation and actions to "
                f"work through each aspect. 150-250 words, no filler."
            )
    else:
        raise HTTPException(400, "Invalid section")
    prompt += get_lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "numerology_interpret", 2, 20)
    await check_not_in_flight(str(current_user.id), "numerology_interpret")
    sys = system_prompt(req.lang) + get_lang_enforce(req.lang)
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    async def stream():
        try:
            async for chunk in safe_groq_stream(msgs, max_tokens=900, lang=req.lang):
                yield chunk
        finally:
            await release_in_flight(str(current_user.id), "numerology_interpret")

    return StreamingResponse(stream(),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
