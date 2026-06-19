import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
            "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


def _sign_index(birth_date: str) -> int:
    _, m, d = birth_date.split("-")
    m, d = int(m), int(d)
    bounds = [(1,20),(2,19),(3,21),(4,20),(5,21),(6,21),(7,23),(8,23),(9,23),(10,23),(11,22),(12,22)]
    indices = [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i, (bm, bd) in enumerate(bounds):
        if m == bm and d < bd:
            return indices[i]
    # fallback: use month-based
    month_signs = [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    return month_signs[m - 1]


def _sun_compat(idx1: int, idx2: int) -> int:
    if idx1 == idx2:
        return 75
    e1, e2 = idx1 % 4, idx2 % 4
    base = 42
    if e1 == e2:
        base = 88
    elif {e1, e2} in ({0, 2}, {1, 3}):
        base = 76
    variation = ((idx1 + 1) * (idx2 + 1)) % 11 - 5
    return max(25, min(98, base + variation))


DESC_HIGH_RU = "Гармоничная пара с глубоким взаимопониманием. Ваши энергии дополняют друг друга."
DESC_MID_RU = "Интересный союз с потенциалом роста. Различия могут обогатить отношения."
DESC_LOW_RU = "Непростое сочетание, требующее терпения и работы над собой. Но именно такие пары часто становятся самыми крепкими."
DESC_HIGH_EN = "A harmonious pair with deep mutual understanding. Your energies complement each other."
DESC_MID_EN = "An interesting union with growth potential. Differences can enrich the relationship."
DESC_LOW_EN = "A challenging combination requiring patience and self-work. But such pairs often become the strongest."


class PersonInput(BaseModel):
    birth_date: str
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None


class CompatRequest(BaseModel):
    person1: PersonInput
    person2: PersonInput
    lang: str = "ru"


@router.post("/compatibility/calculate")
async def calculate(req: CompatRequest):
    idx1 = _sign_index(req.person1.birth_date)
    idx2 = _sign_index(req.person2.birth_date)
    percent = _sun_compat(idx1, idx2)

    if req.lang == "ru":
        desc = DESC_HIGH_RU if percent >= 75 else DESC_MID_RU if percent >= 50 else DESC_LOW_RU
    else:
        desc = DESC_HIGH_EN if percent >= 75 else DESC_MID_EN if percent >= 50 else DESC_LOW_EN

    return {
        "person1_sign": SIGNS_RU[idx1] if req.lang == "ru" else SIGNS[idx1],
        "person1_symbol": SYMBOLS[idx1],
        "person2_sign": SIGNS_RU[idx2] if req.lang == "ru" else SIGNS[idx2],
        "person2_symbol": SYMBOLS[idx2],
        "sun_compatibility": {
            "percent": percent,
            "description": desc,
        },
    }


class InterpretRequest(BaseModel):
    person1: PersonInput
    person2: PersonInput
    lang: str = "ru"


@router.post("/compatibility/interpret")
async def interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    idx1 = _sign_index(req.person1.birth_date)
    idx2 = _sign_index(req.person2.birth_date)
    s1 = SIGNS[idx1]
    s2 = SIGNS[idx2]

    lang_prompt = "на русском" if req.lang == "ru" else "in English"
    prompt = (
        f"Ты — мудрый астролог. Дай интерпретацию совместимости пары: "
        f"{s1} и {s2}. Опиши динамику отношений, сильные стороны и зоны роста. "
        f"80-100 слов, тёплый женственный тон, {lang_prompt}."
    )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=300,
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
