import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel
from typing import Optional

from app.core.deps import get_current_user
from app.core.prompts import system_prompt
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LATIN_VALUES = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    LATIN_VALUES[c] = (i % 9) + 1

CYR_ORDER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
CYR_VALUES = {}
for i, c in enumerate(CYR_ORDER):
    if c in ("Ъ", "Ь"):
        CYR_VALUES[c] = 0
    else:
        CYR_VALUES[c] = (i % 9) + 1

LATIN_VOWELS = set("AEIOU")
CYR_VOWELS = set("АЕЁИОУЫЭЮЯ")

DESCRIPTIONS_RU = {
    1: ("Лидер", "Независимость, амбиции, первопроходец. Вы рождены вести за собой и прокладывать новые пути."),
    2: ("Дипломат", "Гармония, сотрудничество, интуиция. Вы умеете чувствовать людей и находить баланс."),
    3: ("Творец", "Самовыражение, вдохновение, общительность. Ваша творческая энергия заразительна."),
    4: ("Строитель", "Стабильность, дисциплина, трудолюбие. Вы создаёте прочный фундамент для всего."),
    5: ("Искатель", "Свобода, приключения, перемены. Вы не можете стоять на месте и всегда в поиске."),
    6: ("Хранитель", "Забота, ответственность, семья. Вы несёте свет и тепло в жизнь близких."),
    7: ("Мыслитель", "Мудрость, духовность, аналитический ум. Вы ищете глубинный смысл во всём."),
    8: ("Магнат", "Власть, успех, материальное изобилие. Вы умеете притягивать ресурсы."),
    9: ("Гуманист", "Сострадание, мудрость, завершение. Вы служите высшей цели."),
    11: ("Мастер-число: Провидец", "Интуиция высшего порядка, вдохновение, духовное лидерство. Вы видите то, что скрыто от других."),
    22: ("Мастер-число: Зодчий", "Масштабные проекты, материализация мечтаний, практическая мудрость. Вы строите для вечности."),
}

DESCRIPTIONS_EN = {
    1: ("Leader", "Independence, ambition, pioneer. You are born to lead and blaze new trails."),
    2: ("Diplomat", "Harmony, cooperation, intuition. You sense people and find balance effortlessly."),
    3: ("Creator", "Self-expression, inspiration, sociability. Your creative energy is contagious."),
    4: ("Builder", "Stability, discipline, hard work. You create a solid foundation for everything."),
    5: ("Seeker", "Freedom, adventure, change. You can't stand still and are always searching."),
    6: ("Guardian", "Care, responsibility, family. You bring light and warmth to loved ones' lives."),
    7: ("Thinker", "Wisdom, spirituality, analytical mind. You seek deep meaning in everything."),
    8: ("Magnate", "Power, success, material abundance. You know how to attract resources."),
    9: ("Humanitarian", "Compassion, wisdom, completion. You serve a higher purpose."),
    11: ("Master Number: Visionary", "Higher intuition, inspiration, spiritual leadership. You see what is hidden from others."),
    22: ("Master Number: Architect", "Grand projects, manifesting dreams, practical wisdom. You build for eternity."),
}


def _reduce(n: int) -> int:
    while n > 9 and n not in (11, 22):
        n = sum(int(d) for d in str(n))
    return n


def _life_path(birth_date: str) -> int:
    digits = [int(c) for c in birth_date if c.isdigit()]
    return _reduce(sum(digits))


def _name_number(name: str) -> int:
    total = 0
    for c in name.upper():
        total += LATIN_VALUES.get(c, 0) + CYR_VALUES.get(c, 0)
    return _reduce(total)


def _vowel_number(name: str) -> int:
    total = 0
    for c in name.upper():
        if c in LATIN_VOWELS:
            total += LATIN_VALUES.get(c, 0)
        elif c in CYR_VOWELS:
            total += CYR_VALUES.get(c, 0)
    return _reduce(total)


def _consonant_number(name: str) -> int:
    total = 0
    for c in name.upper():
        if c in LATIN_VALUES and c not in LATIN_VOWELS:
            total += LATIN_VALUES[c]
        elif c in CYR_VALUES and c not in CYR_VOWELS and c not in ("Ъ", "Ь"):
            total += CYR_VALUES[c]
    return _reduce(total)


class NumRequest(BaseModel):
    birth_date: str
    full_name: Optional[str] = None
    lang: str = "ru"


@router.post("/numerology/calculate")
async def calculate(
    req: NumRequest,
    current_user: User = Depends(get_current_user),
):
    descs = DESCRIPTIONS_RU if req.lang == "ru" else DESCRIPTIONS_EN
    lp = _life_path(req.birth_date)
    title, desc = descs.get(lp, descs[_reduce(lp)])

    result: dict = {
        "life_path": {"number": lp, "title": title, "description": desc},
    }

    if req.full_name:
        is_pro = current_user.subscription_tier != "free"
        expr = _name_number(req.full_name)
        soul = _vowel_number(req.full_name)
        pers = _consonant_number(req.full_name)
        if is_pro:
            et, ed = descs.get(expr, descs[_reduce(expr)])
            st, sd = descs.get(soul, descs[_reduce(soul)])
            pt, pd = descs.get(pers, descs[_reduce(pers)])
            result["expression"] = {"number": expr, "title": et, "description": ed}
            result["soul_urge"] = {"number": soul, "title": st, "description": sd}
            result["personality"] = {"number": pers, "title": pt, "description": pd}
        else:
            result["expression"] = {"number": expr, "locked": True}
            result["soul_urge"] = {"number": soul, "locked": True}
            result["personality"] = {"number": pers, "locked": True}

    return result


class InterpretRequest(BaseModel):
    birth_date: str
    full_name: Optional[str] = None
    lang: str = "ru"


@router.post("/numerology/interpret")
async def interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    lp = _life_path(req.birth_date)
    parts = [f"Life Path: {lp}"]
    if req.full_name:
        parts.append(f"Expression: {_name_number(req.full_name)}")
        parts.append(f"Soul Urge: {_vowel_number(req.full_name)}")
        parts.append(f"Personality: {_consonant_number(req.full_name)}")

    sys = system_prompt(req.lang)
    name_parts = ""
    if req.full_name:
        name_parts = (
            f"\nЧисло Выражения: {_name_number(req.full_name)}, "
            f"Число Души: {_vowel_number(req.full_name)}"
        ) if req.lang == "ru" else (
            f"\nExpression: {_name_number(req.full_name)}, "
            f"Soul Urge: {_vowel_number(req.full_name)}"
        )

    if req.lang == "ru":
        prompt = (
            f"Число Жизненного Пути: {lp}.{name_parts}\n"
            f"Дай нумерологическую характеристику. Обязательно:\n"
            f"1. Главная жизненная задача этого числа — конкретно\n"
            f"2. Сильные стороны — два-три конкретных качества\n"
            f"3. Скрытые вызовы и как с ними работать\n"
            f"4. В какой сфере реализация наиболее вероятна\n"
            f"Объём: 100-120 слов."
        )
    else:
        prompt = (
            f"Life Path Number: {lp}.{name_parts}\n"
            f"Give a numerological profile. Must include:\n"
            f"1. Core life mission of this number — be specific\n"
            f"2. Strengths — two or three concrete qualities\n"
            f"3. Hidden challenges and how to work with them\n"
            f"4. Which area of life is best for fulfillment\n"
            f"100-120 words."
        )

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=400,
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
