import json
import os
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.prompts import system_prompt
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))


class TarotRequest(BaseModel):
    cards: list[str]
    positions: list[str] = ["прошлое", "настоящее", "будущее"]
    lang: str = "ru"


@router.post("/tarot/interpret")
async def tarot_interpret(
    req: TarotRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier == "free":
        today = date.today().isoformat()
        key = f"tarot_daily:{current_user.id}:{today}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 86400)
        if count > 1:
            raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    cards_desc = ", ".join(
        f"{card} ({pos})" for card, pos in zip(req.cards, req.positions)
    )
    sys = system_prompt(req.lang)

    if req.lang == "ru":
        prompt = (
            f"Расклад Таро: {cards_desc}.\n"
            f"Дай толкование. Обязательно:\n"
            f"1. Что означает каждая карта в своей позиции конкретно\n"
            f"2. Как три карты связаны между собой\n"
            f"3. Один практический вывод для человека\n"
            f"Объём: 90-110 слов. Без общих фраз о 'пути' и 'энергии'."
        )
    else:
        prompt = (
            f"Tarot spread: {cards_desc}.\n"
            f"Give an interpretation. Must include:\n"
            f"1. What each card means in its position specifically\n"
            f"2. How the three cards connect to each other\n"
            f"3. One practical takeaway for the person\n"
            f"90-110 words. No vague phrases about 'paths' and 'energy'."
        )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=250,
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
