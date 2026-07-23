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
from app.core.prompts import lang_enforce as get_lang_enforce, system_prompt
from app.core.structural_i18n import pick, pick_list
from app.data.numerology import life_path as calc_life_path
from app.data.runes import RUNES, SPREADS_RUNES, draw_runes, personal_rune, year_rune
from app.data.runes_i18n import RUNES_I18N, SPREADS_RUNES_I18N, STAVES_I18N
from app.data.staves import STAVES
from app.models.user import RuneReading, User, UserProfile

router = APIRouter()
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")


def _rune_out(rune: dict, lang: str, reversed: bool = False) -> dict:
    key = rune["id"]
    meaning_field = "reversed_meaning" if (reversed and rune["can_reverse"]) else "meaning"
    return {
        "id": rune["id"],
        "index": rune["index"],
        "name": pick(rune, "name", lang, RUNES_I18N, key),
        "symbol": rune["symbol"],
        "keyword": pick(rune, "keyword", lang, RUNES_I18N, key),
        "meaning": pick(rune, meaning_field, lang, RUNES_I18N, key),
        "reversed": reversed,
        "can_reverse": rune["can_reverse"],
        "aett": rune["aett"],
        "element": rune["element"],
        "deity": pick(rune, "deity", lang, RUNES_I18N, key),
        "love": pick(rune, "love", lang, RUNES_I18N, key),
        "career": pick(rune, "career", lang, RUNES_I18N, key),
        "health": pick(rune, "health", lang, RUNES_I18N, key),
        "magic": pick(rune, "magic", lang, RUNES_I18N, key),
        "as_amulet": pick(rune, "as_amulet", lang, RUNES_I18N, key),
    }


def _spread_name(spread_id: str, spread: dict, lang: str) -> str:
    return pick(spread, "name", lang, SPREADS_RUNES_I18N, spread_id)


def _spread_desc(spread_id: str, spread: dict, lang: str) -> str:
    return pick(spread, "desc", lang, SPREADS_RUNES_I18N, spread_id)


def _spread_positions(spread_id: str, spread: dict, lang: str) -> list[str]:
    return pick_list(spread, "positions", lang, SPREADS_RUNES_I18N, spread_id)


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

    drawn = draw_runes(spread["count"])
    positions = _spread_positions(req.spread_type, spread, req.lang)

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
        "spread_name": _spread_name(req.spread_type, spread, req.lang),
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
    session: AsyncSession = Depends(get_session),
):
    # get_current_user pulls a pooled connection via its own Depends(get_session);
    # release it now instead of holding it for the whole SSE stream below.
    await session.close()
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
                f"Начни ответ с «{answer}». Для каждой ключевой руны: исконное значение → применение "
                f"к ситуации. Без мифологических отступлений.\n"
                f"150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Yes/No spread. Runes: {'; '.join(runes_desc)}.{question_part}\n"
                f"Upright runes: {positive} of 3. Answer: {answer_en}.\n"
                f"Start with «{answer_en}». For each key rune: original meaning → application to the "
                f"situation. No mythological digressions.\n"
                f"150-250 words, no filler."
            )
    elif req.spread_type == "yggdrasil":
        if ru:
            prompt = (
                f"Расклад Иггдрасиль (9 миров). Руны:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Разбери по мирам: Асгард (духовное), Мидгард (реальность), Хельхейм (скрытое), "
                f"затем Разум, Сердце, Тело, и временная линия. Для каждой руны: исконное значение → "
                f"применение к ситуации. Без мифологических отступлений.\n"
                f"150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Yggdrasil spread (9 worlds). Runes:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Break down by worlds: Asgard (spiritual), Midgard (reality), Helheim (hidden), "
                f"then Mind, Heart, Body, and timeline. For each rune: original meaning → application "
                f"to the situation. No mythological digressions.\n"
                f"150-250 words, no filler."
            )
    elif req.spread_type == "year_spread":
        if ru:
            prompt = (
                f"Расклад на год. Руны по месяцам:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"Для каждого месяца: исконное значение руны → применение к ситуации. "
                f"Без мифологических отступлений. В конце — общая тема года.\n"
                f"150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Year spread. Runes by month:\n" +
                "\n".join(runes_desc) + f"{question_part}\n"
                f"For each month: the rune's original meaning → application to the situation. "
                f"No mythological digressions. End with the overall year theme.\n"
                f"150-250 words, no filler."
            )
    else:
        spread_name = spread.get("name_ru" if ru else "name_en", req.spread_type)
        if ru:
            prompt = (
                f"Расклад «{spread_name}». Руны: {'; '.join(runes_desc)}.{question_part}\n"
                f"Для каждой руны: исконное значение → применение к ситуации. "
                f"Без мифологических отступлений.\n"
                f"Синтез расклада: общее послание и одна конкретная рекомендация.\n"
                f"150-250 слов, без воды."
            )
        else:
            prompt = (
                f"Spread «{spread_name}». Runes: {'; '.join(runes_desc)}.{question_part}\n"
                f"For each rune: original meaning → application to the situation. "
                f"No mythological digressions.\n"
                f"Spread synthesis: overall message and one specific recommendation.\n"
                f"150-250 words, no filler."
            )
    prompt += get_lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "runes_interpret", 3, 30)
    sys = system_prompt(req.lang) + get_lang_enforce(req.lang)
    if req.spread_type == "year_spread":
        max_tok = 1600
    elif req.spread_type == "yggdrasil":
        max_tok = 1200
    elif req.spread_type == "yes_no":
        max_tok = 600
    else:
        max_tok = 1000
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
    return [
        {
            "id": s["id"],
            "name": pick(s, "name", lang, STAVES_I18N, s["id"]),
            "symbols": s["symbols"],
            "runes_used": s["runes_used"],
            "purpose": pick(s, "purpose", lang, STAVES_I18N, s["id"]),
            "description": pick(s, "description", lang, STAVES_I18N, s["id"]),
            "how_to_use": pick(s, "how_to_use", lang, STAVES_I18N, s["id"]),
        }
        for s in STAVES
    ]


@router.get("/runes/spreads")
async def get_spreads(lang: str = "ru"):
    return [
        {
            "id": k,
            "name": _spread_name(k, s, lang),
            "description": _spread_desc(k, s, lang),
            "icon": s["icon"],
            "count": s["count"],
            "tier": s["tier"],
            "positions": _spread_positions(k, s, lang),
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

    out = []
    for r in readings:
        spread = SPREADS_RUNES.get(r.spread_type, {})
        runes_data = json.loads(r.runes_json) if r.runes_json else []
        preview = [rd.get("id", "") for rd in runes_data[:3]]
        out.append({
            "id": str(r.id),
            "spread_type": r.spread_type,
            "spread_name": _spread_name(r.spread_type, spread, lang) if spread else r.spread_type,
            "question": r.question,
            "rune_preview": preview,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return out
