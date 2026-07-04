import json
import os
import random
from datetime import date
from typing import Optional
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import lang_enforce as get_lang_enforce, system_prompt
from app.models.user import TarotReading, User

router = APIRouter()
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

MAJOR_EN = [
    "The Fool", "The Magician", "High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
]
MAJOR_RU = [
    "Шут", "Маг", "Жрица", "Императрица", "Император",
    "Иерофант", "Влюблённые", "Колесница", "Сила", "Отшельник",
    "Колесо Фортуны", "Справедливость", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир",
]
SUITS_EN = ["Wands", "Cups", "Swords", "Pentacles"]
SUITS_RU = ["Жезлов", "Кубков", "Мечей", "Пентаклей"]
RANKS_EN = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Page", "Knight", "Queen", "King"]
RANKS_RU = ["Туз", "Двойка", "Тройка", "Четвёрка", "Пятёрка", "Шестёрка", "Семёрка",
            "Восьмёрка", "Девятка", "Десятка", "Паж", "Рыцарь", "Королева", "Король"]

CARD_NAMES: dict[int, str] = {}
CARD_NAMES_RU: dict[int, str] = {}
for i, (en, ru) in enumerate(zip(MAJOR_EN, MAJOR_RU)):
    CARD_NAMES[i] = en
    CARD_NAMES_RU[i] = ru
for si in range(4):
    for ri in range(14):
        idx = 22 + si * 14 + ri
        CARD_NAMES[idx] = f"{RANKS_EN[ri]} of {SUITS_EN[si]}"
        CARD_NAMES_RU[idx] = f"{RANKS_RU[ri]} {SUITS_RU[si]}"

SPREADS = {
    "card_of_day":  {"count": 1,  "tier": "free"},
    "three_cards":  {"count": 3,  "tier": "free"},
    "celtic_cross": {"count": 10, "tier": "pro"},
    "horseshoe":    {"count": 7,  "tier": "pro"},
    "relationship": {"count": 7,  "tier": "pro"},
    "yes_no":       {"count": 5,  "tier": "pro"},
    "two_choices":  {"count": 6,  "tier": "pro"},
    "person":       {"count": 5,  "tier": "pro"},
    "year":         {"count": 13, "tier": "pro"},
}


class SpreadRequest(BaseModel):
    spread_id: str
    positions: list[str] = []
    question: Optional[str] = None


class InterpretRequest(BaseModel):
    spread_id: str
    cards: list[dict]
    positions: list[str] = []
    question: Optional[str] = None
    lang: str = "ru"


@router.post("/tarot/spread")
async def tarot_spread(
    req: SpreadRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    spread = SPREADS.get(req.spread_id)
    if not spread:
        raise HTTPException(422, "Unknown spread")

    if spread["tier"] == "pro" and current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    if current_user.subscription_tier == "free":
        today = date.today().isoformat()
        key = f"tarot_{req.spread_id}:{current_user.id}:{today}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 86400)
        if count > 1:
            raise HTTPException(402, "FREE_LIMIT_REACHED")

    count = spread["count"]
    ids = random.sample(range(78), count)
    cards = []
    for card_id in ids:
        cards.append({
            "id": card_id,
            "name": CARD_NAMES.get(card_id, f"Card {card_id}"),
            "name_ru": CARD_NAMES_RU.get(card_id, f"Карта {card_id}"),
            "reversed": random.random() < 0.3,
        })

    reading = TarotReading(
        user_id=current_user.id,
        spread_id=req.spread_id,
        question=req.question,
        cards_json=json.dumps(cards),
    )
    session.add(reading)
    await session.commit()
    await session.refresh(reading)

    return {"cards": cards, "reading_id": str(reading.id)}


@router.post("/tarot/interpret")
async def tarot_interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier == "free":
        today = date.today().isoformat()
        key = f"tarot_interp:{current_user.id}:{today}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 86400)
        if count > 1:
            raise HTTPException(402, "FREE_LIMIT_REACHED")

    cards_desc = []
    upright_count = 0
    for i, card in enumerate(req.cards):
        pos = req.positions[i] if i < len(req.positions) else f"Position {i+1}"
        card_id = card.get("id", -1)
        if req.lang == "ru":
            name = card.get("name_ru") or CARD_NAMES_RU.get(card_id, card.get("name", "?"))
            rev = " (перевёрнутая)" if card.get("reversed") else " (прямая)"
        else:
            name = card.get("name") or CARD_NAMES.get(card_id, "?")
            rev = " (reversed)" if card.get("reversed") else " (upright)"
        if not card.get("reversed"):
            upright_count += 1
        cards_desc.append(f"{name}{rev} — {pos}")

    cards_text = "\n".join(cards_desc)
    sys = system_prompt(req.lang) + get_lang_enforce(req.lang)
    question_part = f'\nВопрос клиента: "{req.question}". Строй ответ вокруг этого вопроса.' if req.question else ""
    yes_no_part = ""

    if req.spread_id == "yes_no":
        answer = "Да" if upright_count >= 3 else "Нет"
        yes_no_part = f"\nЭто расклад Да/Нет. Прямых карт: {upright_count} из {len(req.cards)}. Ответ: {answer}. Начни с чёткого '{answer}'."

    if req.lang == "ru":
        prompt = (
            f"Сделай толкование расклада Таро ({req.spread_id}):\n{cards_text}\n"
            f"Для каждой карты учитывай: позицию в раскладе, прямая/перевёрнутая, масть. "
            f"Перевёрнутая карта = ослабленное/заблокированное/теневое значение.{question_part}{yes_no_part}\n"
            f"Для каждой карты: позиция → значение → связь с вопросом.\n"
            f"Общий вывод — одно предложение, конкретный совет или прогноз, без общих слов.\n"
            f"150-250 слов, без воды. Называй конкретные ситуации."
        )
    else:
        question_part_en = f'\nClient question: "{req.question}". Build your answer around this question.' if req.question else ""
        yes_no_en = ""
        if req.spread_id == "yes_no":
            ans = "Yes" if upright_count >= 3 else "No"
            yes_no_en = f"\nThis is a Yes/No spread. Upright: {upright_count}/{len(req.cards)}. Answer: {ans}. Start with clear '{ans}'."
        prompt = (
            f"Give an interpretation of this tarot spread ({req.spread_id}):\n{cards_text}\n"
            f"For each card consider: position, upright/reversed, suit. "
            f"Reversed = weakened/blocked/shadow meaning.{question_part_en}{yes_no_en}\n"
            f"For each card: position → meaning → connection to the question.\n"
            f"Overall takeaway: one sentence, a specific piece of advice or forecast, no vague words.\n"
            f"150-250 words, no filler. Name concrete situations."
        )
    prompt += get_lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "tarot_interpret", 3, 30)
    max_tokens = 1000 if len(req.cards) <= 5 else 1700
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=max_tokens, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/tarot/history")
async def tarot_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(TarotReading)
        .where(TarotReading.user_id == current_user.id)
        .order_by(TarotReading.created_at.desc())
        .limit(5)
    )
    readings = result.all()
    return [
        {
            "id": str(r.id),
            "spread_id": r.spread_id,
            "question": r.question,
            "cards": json.loads(r.cards_json)[:3],
            "created_at": r.created_at.isoformat(),
        }
        for r in readings
    ]
