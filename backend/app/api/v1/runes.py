import json
import os
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import system_prompt
from app.data.numerology import life_path as calc_life_path
from app.data.runes import RUNES, SPREADS_RUNES, draw_runes, personal_rune, year_rune
from app.data.staves import STAVES
from app.models.user import RuneReading, User, UserProfile

router = APIRouter()
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")


def _rune_out(rune: dict, lang: str, reversed: bool = False) -> dict:
    ru = lang == "ru"
    return {
        "id": rune["id"],
        "index": rune["index"],
        "name": rune["name_ru"] if ru else rune["name_en"],
        "symbol": rune["symbol"],
        "keyword": rune["keyword_ru"] if ru else rune["keyword_en"],
        "meaning": (rune["reversed_meaning_ru"] if ru else rune["reversed_meaning_en"]) if reversed and rune["can_reverse"]
                   else (rune["meaning_ru"] if ru else rune["meaning_en"]),
        "reversed": reversed,
        "can_reverse": rune["can_reverse"],
        "aett": rune["aett"],
        "element": rune["element"],
        "deity": rune["deity"],
        "love": rune["love_ru"] if ru else rune["love_en"],
        "career": rune["career_ru"] if ru else rune["career_en"],
        "health": rune["health_ru"] if ru else rune["health_en"],
        "magic": rune["magic_ru"] if ru else rune["magic_en"],
        "as_amulet": rune["as_amulet_ru"] if ru else rune["as_amulet_en"],
    }


class DrawRequest(BaseModel):
    spread_type: str = "rune_of_day"
    question: Optional[str] = None
    lang: str = "ru"


@router.post("/runes/draw")
async def draw(
    req: DrawRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    spread = SPREADS_RUNES.get(req.spread_type)
    if not spread:
        raise HTTPException(400, "Invalid spread type")

    is_pro = current_user.subscription_tier != "free"
    if spread["tier"] == "pro" and not is_pro:
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    if not is_pro and req.spread_type in ("rune_of_day", "three_norns"):
        r = aioredis.from_url(redis_url)
        try:
            today = date.today().isoformat()
            key = f"runes_daily:{req.spread_type}:{current_user.id}:{today}"
            n = await r.incr(key)
            if n == 1:
                await r.expire(key, 86400)
            if n > 1:
                raise HTTPException(402, "FREE_LIMIT_REACHED")
        finally:
            await r.close()

    ru = req.lang == "ru"
    drawn = draw_runes(spread["count"])
    positions = spread["positions_ru"] if ru else spread["positions_en"]

    result_runes = []
    for i, d in enumerate(drawn):
        pos_name = positions[i] if i < len(positions) else f"#{i+1}"
        out = _rune_out(d["rune"], req.lang, d["reversed"])
        out["position_name"] = pos_name
        result_runes.append(out)

    reading = RuneReading(
        user_id=current_user.id,
        spread_type=req.spread_type,
        question=req.question,
        runes_json=json.dumps([{"id": r["id"], "reversed": r["reversed"], "position": r["position_name"]} for r in result_runes], ensure_ascii=False),
    )
    session.add(reading)
    await session.commit()

    return {
        "spread_type": req.spread_type,
        "spread_name": spread["name_ru"] if ru else spread["name_en"],
        "positions": positions,
        "drawn_runes": result_runes,
        "question": req.question,
    }


class InterpretRequest(BaseModel):
    spread_type: str
    drawn_runes: list[dict]
    question: Optional[str] = None
    lang: str = "ru"


@router.post("/runes/interpret")
async def interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
):
    if req.spread_type != "rune_of_day" and current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    spread = SPREADS_RUNES.get(req.spread_type, {})
    ru = req.lang == "ru"

    runes_desc = []
    for r in req.drawn_runes:
        pos = r.get("position_name", "")
        name = r.get("name", r.get("id", "?"))
        state = ("перевёрнутая" if ru else "reversed") if r.get("reversed") else ("прямая" if ru else "upright")
        runes_desc.append(f"{pos}: {name} ({state})")

    question_part = ""
    if req.question:
        question_part = f'\nВопрос: "{req.question}".' if ru else f'\nQuestion: "{req.question}".'

    if req.spread_type == "yes_no":
        positive = sum(1 for r in req.drawn_runes if not r.get("reversed"))
        answer = "ДА" if positive >= 2 else "НЕТ"
        answer_en = "YES" if positive >= 2 else "NO"
        if ru:
            prompt = (
                f"Расклад Да/Нет. Руны: {'; '.join(runes_desc)}.{question_part}\n"
                f"Прямых рун: {positive} из 3. Ответ: {answer}.\n"
                f"Начни ответ с крупного «{answer}». Объясни почему руны так ответили. "
                f"80-100 слов. Стиль: мудрый северный наставник."
            )
        else:
            prompt = (
                f"Yes/No spread. Runes: {'; '.join(runes_desc)}.{question_part}\n"
                f"Upright runes: {positive} of 3. Answer: {answer_en}.\n"
                f"Start with a big «{answer_en}». Explain why the runes answered this way. "
                f"80-100 words. Style: wise Norse mentor."
            )
    elif req.spread_type == "yggdrasil":
        if ru:
            prompt = (
                f"Расклад Иггдрасиль (9 миров). Руны:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Разбери по мирам: Асгард (духовное), Мидгард (реальность), Хельхейм (скрытое), "
                f"затем Разум, Сердце, Тело, и временная линия. "
                f"150-180 слов. Стиль: мудрый северный наставник."
            )
        else:
            prompt = (
                f"Yggdrasil spread (9 worlds). Runes:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Break down by worlds: Asgard (spiritual), Midgard (reality), Helheim (hidden), "
                f"then Mind, Heart, Body, and timeline. "
                f"150-180 words. Style: wise Norse mentor."
            )
    elif req.spread_type == "year_spread":
        if ru:
            prompt = (
                f"Расклад на год. Руны по месяцам:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Дай краткий прогноз по каждому месяцу (1-2 предложения) и общую тему года. "
                f"200-250 слов. Стиль: мудрый северный наставник."
            )
        else:
            prompt = (
                f"Year spread. Runes by month:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Give a brief forecast for each month (1-2 sentences) and overall year theme. "
                f"200-250 words. Style: wise Norse mentor."
            )
    else:
        spread_name = spread.get("name_ru" if ru else "name_en", req.spread_type)
        if ru:
            prompt = (
                f"Расклад «{spread_name}». Руны: {'; '.join(runes_desc)}.{question_part}\n"
                f"Дай толкование:\n"
                f"1. Значение каждой руны в её позиции\n"
                f"2. Общий посыл расклада\n"
                f"3. Конкретная рекомендация\n"
                f"100-130 слов. Стиль: мудрый северный наставник."
            )
        else:
            prompt = (
                f"Spread «{spread_name}». Runes: {'; '.join(runes_desc)}.{question_part}\n"
                f"Give interpretation:\n"
                f"1. Meaning of each rune in its position\n"
                f"2. Overall spread message\n"
                f"3. Specific recommendation\n"
                f"100-130 words. Style: wise Norse mentor."
            )

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "runes_interpret", 3, 30)
    lang_enforce = " Отвечай ТОЛЬКО на русском." if ru else " Answer ONLY in English."
    sys = system_prompt(req.lang) + lang_enforce
    max_tok = 600 if req.spread_type == "year_spread" else 400
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=max_tok, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/runes/personal")
async def get_personal_rune(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result_q = await session.exec(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result_q.first()
    if not profile or not profile.birth_date:
        raise HTTPException(400, "birth_date required")

    lp = calc_life_path(profile.birth_date)
    lang = current_user.lang or "ru"

    pr = personal_rune(lp)
    yr = year_rune(date.today().year)

    return {
        "life_path": lp,
        "personal_rune": _rune_out(pr, lang),
        "year_rune": _rune_out(yr, lang),
        "year": date.today().year,
    }


@router.get("/runes/staves")
async def get_staves(lang: str = "ru"):
    ru = lang == "ru"
    return [
        {
            "id": s["id"],
            "name": s["name_ru"] if ru else s["name_en"],
            "symbols": s["symbols"],
            "runes_used": s["runes_used"],
            "purpose": s["purpose_ru"] if ru else s["purpose_en"],
            "description": s["description_ru"] if ru else s["description_en"],
            "how_to_use": s["how_to_use_ru"] if ru else s["how_to_use_en"],
        }
        for s in STAVES
    ]


@router.get("/runes/spreads")
async def get_spreads(lang: str = "ru"):
    ru = lang == "ru"
    return [
        {
            "id": k,
            "name": s["name_ru"] if ru else s["name_en"],
            "description": s["desc_ru"] if ru else s["desc_en"],
            "icon": s["icon"],
            "count": s["count"],
            "tier": s["tier"],
            "positions": s["positions_ru"] if ru else s["positions_en"],
        }
        for k, s in SPREADS_RUNES.items()
    ]


@router.get("/runes/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result_q = await session.exec(
        select(RuneReading)
        .where(RuneReading.user_id == current_user.id)
        .order_by(col(RuneReading.created_at).desc())
        .limit(5)
    )
    readings = result_q.all()
    lang = current_user.lang or "ru"
    ru = lang == "ru"

    out = []
    for r in readings:
        spread = SPREADS_RUNES.get(r.spread_type, {})
        runes_data = json.loads(r.runes_json) if r.runes_json else []
        preview = [rd.get("id", "") for rd in runes_data[:3]]
        out.append({
            "id": str(r.id),
            "spread_type": r.spread_type,
            "spread_name": spread.get("name_ru" if ru else "name_en", r.spread_type),
            "question": r.question,
            "rune_preview": preview,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return out
