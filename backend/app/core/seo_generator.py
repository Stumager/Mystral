import asyncio
import json
import logging
import re
from datetime import datetime, timedelta

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import SeoContent

logger = logging.getLogger(__name__)

_CLEAN_RE = re.compile(r'[^ -~ -\xffЀ-ӿ\n\r\t«»„""\'\'–—…°%№♈-♓☽✦★{}:,\[\]"]')

_QUALITY = (
    "Каждая секция должна содержать не менее 150 слов. Итоговый текст — не менее 1000 слов. "
    "Избегай воды и общих фраз. Каждое предложение должно нести конкретную информацию. "
    "Используй ТОЛЬКО кириллицу, стандартные знаки препинания и цифры. "
)

PROMPTS = {
    "zodiac": (
        "Напиши подробную характеристику знака зодиака {name} ({dates}, стихия {element}, планета {ruler}). "
        "Включи секции: 1) Описание характера, 2) Сильные стороны, 3) Слабые стороны, "
        "4) В любви и отношениях, 5) В карьере, 6) Совместимость с другими знаками, "
        "7) Здоровье и самочувствие, 8) Финансы и деньги, 9) Знаменитые {name}, 10) Советы. "
        "Создай 5 FAQ с ответами. " + _QUALITY +
        "Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
        "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}"
    ),
    "tarot": (
        "Напиши подробное значение карты Таро «{name_ru}». "
        "Включи секции: 1) Значение в прямом положении, 2) Значение в обратном положении, "
        "3) В любви и отношениях, 4) В карьере и финансах, 5) Совет карты, 6) Сочетания с другими картами. "
        "Создай 5 FAQ. " + _QUALITY +
        "Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
        "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}"
    ),
    "rune": (
        "Напиши подробное значение руны {name} ({symbol}). "
        "Включи секции: 1) Происхождение и этимология, 2) Магическое значение, "
        "3) Значение в гадании прямая, 4) Значение в гадании обратная, "
        "5) Применение в ставах и биндрунах, 6) Руна как амулет. "
        "Создай 5 FAQ. " + _QUALITY +
        "Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
        "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}"
    ),
    "numerology": (
        "Напиши подробное значение числа жизненного пути {number} — «{name}». "
        "Включи секции: 1) Характер и личность, 2) Жизненное предназначение, "
        "3) Карьера и призвание, 4) Любовь и отношения, 5) Здоровье, "
        "6) Известные люди с этим числом. "
        "Создай 5 FAQ. " + _QUALITY +
        "Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
        "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}"
    ),
}

FALLBACK = json.dumps({
    "intro": "Подробная информация скоро появится. Зарегистрируйтесь в Mystral для персонального анализа.",
    "sections": [{"title": "Описание", "text": "Контент генерируется. Пожалуйста, зайдите позже."}],
    "faq": [{"q": "Как узнать больше?", "a": "Зарегистрируйтесь в Mystral для персонального анализа."}],
    "cta_text": "Откройте Mystral для персонального эзотерического анализа.",
}, ensure_ascii=False)


async def get_seo_content(page_type: str, slug: str, data: dict, session: AsyncSession) -> dict:
    result = await session.exec(
        select(SeoContent).where(SeoContent.page_type == page_type, SeoContent.slug == slug, SeoContent.lang == "ru")
    )
    cached = result.first()

    if cached and cached.generated_at and cached.generated_at > datetime.utcnow() - timedelta(days=30):
        try:
            logger.debug("Cache hit for %s/%s", page_type, slug)
            return json.loads(cached.content)
        except Exception:
            pass

    prompt_tpl = PROMPTS.get(page_type, "")
    if not prompt_tpl:
        return json.loads(FALLBACK)

    prompt = prompt_tpl.format(**data)

    try:
        from app.core.groq_client import _get_client
        client = _get_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты SEO-копирайтер для эзотерического сайта Mystral. Пиши на русском. Отвечай строго JSON. Никаких иероглифов или символов других алфавитов."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=0.7,
        )
        raw = _CLEAN_RE.sub('', resp.choices[0].message.content or "")
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end])
        else:
            return json.loads(FALLBACK)
    except Exception as e:
        logger.error("SEO gen error for %s/%s: %s", page_type, slug, e)
        return json.loads(FALLBACK)

    content_str = json.dumps(parsed, ensure_ascii=False)
    if cached:
        cached.content = content_str
        cached.generated_at = datetime.utcnow()
        session.add(cached)
    else:
        session.add(SeoContent(page_type=page_type, slug=slug, lang="ru", content=content_str))
    await session.commit()
    logger.info("Generated SEO content for %s/%s", page_type, slug)
    return parsed


async def warm_seo_cache() -> None:
    from app.core.database import get_session_context
    from app.data.seo_data import NUMEROLOGY_SEO, RUNE_SEO, TAROT_CARDS, ZODIAC_SIGNS

    items: list[tuple[str, str, dict]] = []
    for s in ZODIAC_SIGNS:
        items.append(("zodiac", s["slug"], s))
    for c in TAROT_CARDS:
        items.append(("tarot", c["slug"], c))
    for r in RUNE_SEO:
        items.append(("rune", r["slug"], r))
    for n in NUMEROLOGY_SEO:
        items.append(("numerology", n["slug"], n))

    total = len(items)
    logger.info("SEO cache warm: starting %d pages", total)

    for i, (ptype, slug, data) in enumerate(items):
        async with get_session_context() as session:
            result = await session.exec(
                select(SeoContent).where(SeoContent.page_type == ptype, SeoContent.slug == slug)
            )
            if result.first():
                continue
            try:
                await get_seo_content(ptype, slug, data, session)
                logger.info("SEO cache warm: %s/%s (%d/%d)", ptype, slug, i + 1, total)
            except Exception as e:
                logger.error("SEO warm error %s/%s: %s", ptype, slug, e)
        await asyncio.sleep(2)

    logger.info("SEO cache warm: done")
