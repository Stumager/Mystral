import json
import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TONES = {
    "ru": "мягко, образно, с душой, на русском языке",
    "en": "empowering and mystical, in English",
}


class TarotRequest(BaseModel):
    cards: list[str]
    positions: list[str] = ["прошлое", "настоящее", "будущее"]
    lang: str = "ru"


@router.post("/tarot/interpret")
async def tarot_interpret(req: TarotRequest):
    cards_desc = ", ".join(
        f"{card} ({pos})" for card, pos in zip(req.cards, req.positions)
    )
    tone = TONES.get(req.lang, TONES["ru"])

    prompt = (
        f"Дай толкование расклада Таро: {cards_desc}. "
        f"Объясни что означает каждая карта в своей позиции "
        f"и как они связаны между собой. "
        f"Тон: {tone}. "
        f"Объём: 80-100 слов. Без вступлений сразу по делу."
    )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
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
