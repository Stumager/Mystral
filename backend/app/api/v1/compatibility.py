import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.prompts import system_prompt
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
            "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


SIGN_RANGES = [
    #  index, from_month, from_day, to_month, to_day
    (9,  1, 1,   1, 19),   # Capricorn
    (10, 1, 20,  2, 18),   # Aquarius
    (11, 2, 19,  3, 20),   # Pisces
    (0,  3, 21,  4, 19),   # Aries
    (1,  4, 20,  5, 20),   # Taurus
    (2,  5, 21,  6, 20),   # Gemini
    (3,  6, 21,  7, 22),   # Cancer
    (4,  7, 23,  8, 22),   # Leo
    (5,  8, 23,  9, 22),   # Virgo
    (6,  9, 23,  10, 22),  # Libra
    (7,  10, 23, 11, 21),  # Scorpio
    (8,  11, 22, 12, 21),  # Sagittarius
    (9,  12, 22, 12, 31),  # Capricorn
]


def _sign_index(birth_date: str) -> int:
    _, m, d = birth_date.split("-")
    m, d = int(m), int(d)
    for idx, fm, fd, tm, td in SIGN_RANGES:
        after_from = m > fm or (m == fm and d >= fd)
        before_to = m < tm or (m == tm and d <= td)
        if after_from and before_to:
            return idx
    return 9


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

    sys = system_prompt(req.lang)

    if req.lang == "ru":
        prompt = (
            f"Синастрия: первый человек — Солнце {s1}, второй — Солнце {s2}.\n"
            f"Опиши совместимость. Обязательно:\n"
            f"1. В чём сила этой пары конкретно\n"
            f"2. Главный источник конфликтов\n"
            f"3. Что помогает — один практический совет\n"
            f"Объём: 90-110 слов. Говори 'вы' обращаясь к паре."
        )
    else:
        prompt = (
            f"Synastry: first person — Sun in {s1}, second — Sun in {s2}.\n"
            f"Describe their compatibility. Must include:\n"
            f"1. The specific strength of this pair\n"
            f"2. The main source of conflicts\n"
            f"3. One practical tip that helps\n"
            f"90-110 words. Address as 'you' speaking to the couple."
        )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=300,
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
