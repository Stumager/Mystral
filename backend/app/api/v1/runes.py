import json
import os
import random
from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

RUNES = [
    {"id": "fehu",     "name_ru": "Феху",     "name_en": "Fehu",     "symbol": "ᚠ",
     "meaning_ru": "Богатство, успех, изобилие", "meaning_en": "Wealth, success, abundance",
     "rev_ru": "Потери, жадность, застой", "rev_en": "Loss, greed, stagnation"},
    {"id": "uruz",     "name_ru": "Уруз",     "name_en": "Uruz",     "symbol": "ᚢ",
     "meaning_ru": "Сила, здоровье, выносливость", "meaning_en": "Strength, health, endurance",
     "rev_ru": "Слабость, болезнь, упущенные возможности", "rev_en": "Weakness, illness, missed chances"},
    {"id": "thurisaz", "name_ru": "Турисаз",  "name_en": "Thurisaz", "symbol": "ᚦ",
     "meaning_ru": "Защита, разрушение преград, сила воли", "meaning_en": "Protection, breaking barriers, willpower",
     "rev_ru": "Уязвимость, опасность, необдуманность", "rev_en": "Vulnerability, danger, recklessness"},
    {"id": "ansuz",    "name_ru": "Ансуз",    "name_en": "Ansuz",    "symbol": "ᚨ",
     "meaning_ru": "Мудрость, общение, вдохновение", "meaning_en": "Wisdom, communication, inspiration",
     "rev_ru": "Обман, непонимание, манипуляции", "rev_en": "Deception, misunderstanding, manipulation"},
    {"id": "raido",    "name_ru": "Райдо",    "name_en": "Raido",    "symbol": "ᚱ",
     "meaning_ru": "Путешествие, движение, прогресс", "meaning_en": "Journey, movement, progress",
     "rev_ru": "Застой, задержки, неверный путь", "rev_en": "Stagnation, delays, wrong path"},
    {"id": "kenaz",    "name_ru": "Кеназ",    "name_en": "Kenaz",    "symbol": "ᚲ",
     "meaning_ru": "Знание, творчество, просветление", "meaning_en": "Knowledge, creativity, enlightenment",
     "rev_ru": "Тьма, невежество, творческий блок", "rev_en": "Darkness, ignorance, creative block"},
    {"id": "gebo",     "name_ru": "Гебо",     "name_en": "Gebo",     "symbol": "ᚷ",
     "meaning_ru": "Дар, партнёрство, равновесие", "meaning_en": "Gift, partnership, balance",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "wunjo",    "name_ru": "Вуньо",    "name_en": "Wunjo",    "symbol": "ᚹ",
     "meaning_ru": "Радость, гармония, счастье", "meaning_en": "Joy, harmony, happiness",
     "rev_ru": "Печаль, кризис, разочарование", "rev_en": "Sorrow, crisis, disappointment"},
    {"id": "hagalaz",  "name_ru": "Хагалаз",  "name_en": "Hagalaz",  "symbol": "ᚺ",
     "meaning_ru": "Разрушение, трансформация, стихия", "meaning_en": "Destruction, transformation, elemental force",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "nauthiz",  "name_ru": "Наутиз",   "name_en": "Nauthiz",  "symbol": "ᚾ",
     "meaning_ru": "Необходимость, терпение, ограничения", "meaning_en": "Necessity, patience, constraints",
     "rev_ru": "Нетерпение, лень, провал", "rev_en": "Impatience, laziness, failure"},
    {"id": "isa",      "name_ru": "Иса",      "name_en": "Isa",      "symbol": "ᛁ",
     "meaning_ru": "Лёд, пауза, самоанализ", "meaning_en": "Ice, pause, self-reflection",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "jera",     "name_ru": "Йера",     "name_en": "Jera",     "symbol": "ᛃ",
     "meaning_ru": "Урожай, цикл, награда за труд", "meaning_en": "Harvest, cycle, reward for effort",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "eihwaz",   "name_ru": "Эйваз",   "name_en": "Eihwaz",   "symbol": "ᛇ",
     "meaning_ru": "Стойкость, защита, связь миров", "meaning_en": "Resilience, protection, world connection",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "perthro",  "name_ru": "Перт",     "name_en": "Perthro",  "symbol": "ᛈ",
     "meaning_ru": "Тайна, судьба, скрытое знание", "meaning_en": "Mystery, fate, hidden knowledge",
     "rev_ru": "Застой, секреты, разочарование", "rev_en": "Stagnation, secrets, disappointment"},
    {"id": "algiz",    "name_ru": "Альгиз",   "name_en": "Algiz",    "symbol": "ᛉ",
     "meaning_ru": "Защита, духовная связь, инстинкт", "meaning_en": "Protection, spiritual connection, instinct",
     "rev_ru": "Уязвимость, скрытая опасность", "rev_en": "Vulnerability, hidden danger"},
    {"id": "sowilo",   "name_ru": "Совило",   "name_en": "Sowilo",   "symbol": "ᛊ",
     "meaning_ru": "Солнце, победа, жизненная сила", "meaning_en": "Sun, victory, life force",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "tiwaz",    "name_ru": "Тиваз",    "name_en": "Tiwaz",    "symbol": "ᛏ",
     "meaning_ru": "Справедливость, честь, победа", "meaning_en": "Justice, honor, victory",
     "rev_ru": "Несправедливость, поражение, жертва", "rev_en": "Injustice, defeat, sacrifice"},
    {"id": "berkano",  "name_ru": "Беркано",  "name_en": "Berkano",  "symbol": "ᛒ",
     "meaning_ru": "Рождение, рост, женственность", "meaning_en": "Birth, growth, femininity",
     "rev_ru": "Бесплодие, застой, конфликт в семье", "rev_en": "Infertility, stagnation, family conflict"},
    {"id": "ehwaz",    "name_ru": "Эваз",     "name_en": "Ehwaz",    "symbol": "ᛖ",
     "meaning_ru": "Движение, прогресс, доверие", "meaning_en": "Movement, progress, trust",
     "rev_ru": "Застой, недоверие, разрыв", "rev_en": "Stagnation, mistrust, break"},
    {"id": "mannaz",   "name_ru": "Манназ",   "name_en": "Mannaz",   "symbol": "ᛗ",
     "meaning_ru": "Человек, самопознание, разум", "meaning_en": "Human, self-knowledge, mind",
     "rev_ru": "Одиночество, эгоизм, заблуждение", "rev_en": "Loneliness, selfishness, delusion"},
    {"id": "laguz",    "name_ru": "Лагуз",    "name_en": "Laguz",    "symbol": "ᛚ",
     "meaning_ru": "Вода, интуиция, подсознание", "meaning_en": "Water, intuition, subconscious",
     "rev_ru": "Страх, иллюзии, потеря пути", "rev_en": "Fear, illusions, losing the way"},
    {"id": "ingwaz",   "name_ru": "Ингваз",   "name_en": "Ingwaz",   "symbol": "ᛜ",
     "meaning_ru": "Плодородие, завершение цикла, покой", "meaning_en": "Fertility, cycle completion, peace",
     "rev_ru": "—", "rev_en": "—"},
    {"id": "othala",   "name_ru": "Отала",    "name_en": "Othala",   "symbol": "ᛟ",
     "meaning_ru": "Наследие, дом, предки", "meaning_en": "Heritage, home, ancestors",
     "rev_ru": "Потеря дома, отчуждение, бездомность", "rev_en": "Loss of home, alienation, homelessness"},
    {"id": "dagaz",    "name_ru": "Дагаз",    "name_en": "Dagaz",    "symbol": "ᛞ",
     "meaning_ru": "Рассвет, прорыв, трансформация", "meaning_en": "Dawn, breakthrough, transformation",
     "rev_ru": "—", "rev_en": "—"},
]

NO_REVERSE = {"gebo", "hagalaz", "isa", "jera", "eihwaz", "sowilo", "ingwaz", "dagaz"}


class DrawRequest(BaseModel):
    count: int = 1
    lang: str = "ru"


@router.post("/runes/draw")
async def draw(
    req: DrawRequest,
    current_user: User = Depends(get_current_user),
):
    count = max(1, min(req.count, 3))
    is_pro = current_user.subscription_tier != "free"

    if not is_pro:
        count = 1
        today = date.today().isoformat()
        key = f"runes_daily:{current_user.id}:{today}"
        n = await redis_client.incr(key)
        if n == 1:
            await redis_client.expire(key, 86400)
        if n > 1:
            raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    drawn = random.sample(RUNES, count)
    result = []
    for rune in drawn:
        can_reverse = rune["id"] not in NO_REVERSE
        is_reversed = can_reverse and random.random() < 0.3
        lang = req.lang
        entry = {
            "id": rune["id"],
            "name": rune[f"name_{lang}"] if f"name_{lang}" in rune else rune["name_en"],
            "symbol": rune["symbol"],
            "reversed": is_reversed,
            "meaning": rune[f"rev_{lang}"] if is_reversed else rune[f"meaning_{lang}"],
        }
        result.append(entry)

    return {"runes": result}


class InterpretRequest(BaseModel):
    runes: list[dict]
    lang: str = "ru"


@router.post("/runes/interpret")
async def interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
):
    parts = []
    for r in req.runes:
        pos = "reversed" if r.get("reversed") else "upright"
        parts.append(f"{r.get('name', '?')} ({pos})")

    lang_prompt = "на русском" if req.lang == "ru" else "in English"
    prompt = (
        f"Ты — мудрый рунолог-провидец. Выпали руны: {', '.join(parts)}. "
        f"Дай глубокое толкование расклада. Свяжи значения рун в единое послание. "
        f"80-100 слов, загадочный мудрый Nordic стиль, {lang_prompt}."
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
