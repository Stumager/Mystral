import json
import logging
import os
import re
from datetime import datetime, timedelta

_CLEAN_RE = re.compile(r'[^ -~ -\xffЀ-ӿ\n\r\t«»„""\'\'–—…°%№♈-♓☽✦★{}:,\[\]"]')

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import SeoContent

logger = logging.getLogger(__name__)

PROMPTS = {
    "zodiac": "Напиши подробную характеристику знака зодиака {name} ({dates}, стихия {element}, планета {ruler}). "
              "Включи: 1) описание характера (100 слов), 2) сильные стороны, 3) слабые стороны, "
              "4) в любви и отношениях, 5) в карьере, 6) совместимость с другими знаками, 7) советы. "
              "Также создай 5 вопросов FAQ с ответами. Стиль — мистический но доступный. "
              "Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
              "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}",
    "tarot": "Напиши подробное значение карты Таро «{name_ru}». "
             "Включи: значение в прямом положении, в обратном, в любви, карьере, финансах, совете. "
             "Создай 5 FAQ. Стиль — авторитетный, эзотерический. "
             "Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
             "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}",
    "rune": "Напиши подробное значение руны {name} ({symbol}). "
            "Включи: происхождение, магическое значение, значение в гадании прямая/обратная, применение в ставах. "
            "Создай 5 FAQ. Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
            "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}",
    "numerology": "Напиши подробное значение числа жизненного пути {number} — «{name}». "
                  "Включи: характер, предназначение, карьера, отношения, известные люди. "
                  "Создай 5 FAQ. Верни JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
                  "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}",
}

FALLBACK = json.dumps({
    "intro": "Подробная информация скоро появится. Зарегистрируйтесь в Mystral для персонального анализа.",
    "sections": [{"title": "Описание", "text": "Контент генерируется. Пожалуйста, зайдите позже."}],
    "faq": [{"q": "Как узнать больше?", "a": "Зарегистрируйтесь в Mystral для персонального анализа."}],
    "cta_text": "Откройте Mystral для персонального эзотерического анализа.",
}, ensure_ascii=False)


async def get_seo_content(page_type: str, slug: str, data: dict, session: AsyncSession) -> dict:
    result = await session.exec(
        select(SeoContent).where(
            SeoContent.page_type == page_type,
            SeoContent.slug == slug,
            SeoContent.lang == "ru",
        )
    )
    cached = result.first()

    if cached and cached.generated_at and cached.generated_at > datetime.utcnow() - timedelta(days=30):
        try:
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
                {"role": "system", "content": "Ты SEO-копирайтер для эзотерического сайта Mystral. Пиши на русском. Отвечай строго JSON."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        raw = _CLEAN_RE.sub('', resp.choices[0].message.content or "")
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            content_json = raw[start:end]
            parsed = json.loads(content_json)
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

    return parsed
