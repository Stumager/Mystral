import logging
from datetime import date

from app.core.groq_client import _get_async_client
from app.core.prompts import lang_enforce, system_prompt

logger = logging.getLogger(__name__)

# A production push notification was observed cut off mid-sentence ("...day
# for" with nothing after it) — the same max_tokens-too-tight class of bug
# fixed for SEO generation (TZ-060). 200 was not enough margin for a 60-70
# word response, especially in Cyrillic where this tokenizer needs more
# tokens per word than for English. max_tokens is a ceiling, not a cost — a
# short response that finishes well under this isn't billed any differently.
GENERATION_MAX_TOKENS = 500

SIGNS_DATA = [
    (1, 1, 1, 19, "capricorn"), (1, 20, 2, 18, "aquarius"), (2, 19, 3, 20, "pisces"),
    (3, 21, 4, 19, "aries"), (4, 20, 5, 20, "taurus"), (5, 21, 6, 20, "gemini"),
    (6, 21, 7, 22, "cancer"), (7, 23, 8, 22, "leo"), (8, 23, 9, 22, "virgo"),
    (9, 23, 10, 22, "libra"), (10, 23, 11, 21, "scorpio"), (11, 22, 12, 21, "sagittarius"),
    (12, 22, 12, 31, "capricorn"),
]

SIGNS_RU = {
    "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы", "cancer": "Рак",
    "leo": "Лев", "virgo": "Дева", "libra": "Весы", "scorpio": "Скорпион",
    "sagittarius": "Стрелец", "capricorn": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы",
}

SIGNS_EMOJI = {
    "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋",
    "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
    "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓",
}


def zodiac_from_date(d: date) -> str:
    m, day = d.month, d.day
    for fm, fd, tm, td, sign in SIGNS_DATA:
        if (m > fm or (m == fm and day >= fd)) and (m < tm or (m == tm and day <= td)):
            return sign
    return "capricorn"


async def generate_horoscope(sign: str, lang: str) -> str:
    sign_name = SIGNS_RU.get(sign, sign)
    today = date.today().isoformat()
    sys = system_prompt(lang) + lang_enforce(lang)

    if lang == "ru":
        prompt = (
            f"Знак: {sign_name}. Дата: {today}.\n"
            f"Напиши гороскоп на день. Обязательно укажи:\n"
            f"1. Одну конкретную сферу жизни (работа/отношения/финансы/здоровье)\n"
            f"2. Один конкретный совет что сделать или избежать\n"
            f"3. Благоприятное время дня если уместно\n"
            f"Объём: 60-70 слов. Без вступлений типа 'Дорогой Скорпион'."
        )
    else:
        prompt = (
            f"Sign: {sign.capitalize()}. Date: {today}.\n"
            f"Write a daily horoscope. Must include:\n"
            f"1. One specific life area (work/relationships/finances/health)\n"
            f"2. One concrete tip — what to do or avoid\n"
            f"3. Best time of day if relevant\n"
            f"60-70 words. No greetings like 'Dear Scorpio'."
        )

    client = _get_async_client()
    response = await client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": prompt},
        ],
        stream=False,
        max_tokens=GENERATION_MAX_TOKENS,
    )
    if getattr(response.choices[0], "finish_reason", None) == "length":
        logger.warning("Daily horoscope for %s/%s truncated by max_tokens (finish_reason=length)", sign, lang)
    return response.choices[0].message.content or ""
