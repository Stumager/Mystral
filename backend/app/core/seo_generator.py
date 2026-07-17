import asyncio
import json
import logging
import re
from datetime import datetime, timedelta

import json_repair
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.user import SeoContent

logger = logging.getLogger(__name__)

# Latin Extended-A (Ā-ſ) is required for Turkish ğ/ş/ı/İ — plain Latin-1
# does not contain them and they would be stripped from generated content.
_CLEAN_RE = re.compile(r'[^ -~ -\xffĀ-ſЀ-ӿ\n\r\t«»„""\'\'–—…°%№♈-♓☽✦★{}:,\[\]"]')

_QUALITY = (
    "Каждая секция должна содержать не менее 150 слов. Итоговый текст — не менее 1000 слов. "
    "Избегай воды и общих фраз. Каждое предложение должно нести конкретную информацию. "
    "Используй ТОЛЬКО кириллицу, стандартные знаки препинания и цифры. "
    "В значениях JSON-строк никогда не используй символ прямой двойной кавычки \" — "
    "для выделения слов используй «ёлочки» или одинарные кавычки. "
    "Пример корректного значения: \"Овен часто называют «первопроходцем» зодиака.\" "
    "Пиши уверенно и окончательно — никогда не исправляй себя вслух в тексте "
    "(никаких фраз вида «нет, на самом деле» или «поправка», «хотя нет»). "
    "В пункте про известных людей приведи ровно 3–4 реальных имени с одной короткой "
    "фразой о каждом, не обсуждая и не подвергая сомнению точность дат рождения."
)

# TZ-060: response_format=json_object (see _generate_and_store) already forces
# syntactically valid JSON at the API level — this instruction is defense in
# depth against the model still choosing bad content inside a valid string
# (e.g. a literal " it would otherwise need to escape).
# Russian topic/section prompts stay byte-identical — zero behavior change for ru pages.
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

# For the 5 prefixed languages: English master templates with an explicit
# target-language directive produce far better native-quality output from
# deepseek-class models than a Russian prompt with "translate to X" appended.
# Data passed in is already localized, so {name} etc. are target-language names.
_LANG_NAME = {"en": "English", "es": "Spanish", "pt": "Brazilian Portuguese", "tr": "Turkish", "uk": "Ukrainian"}

_QUALITY_I18N = (
    "Each section must contain at least 150 words; the full text must be at least 1000 words. "
    "Avoid filler and generic phrases — every sentence must carry specific information. "
    "Write ALL output in {language}: native-sounding, not a literal translation. "
    "Use only standard punctuation and digits. "
    "Inside JSON string values, never use a literal straight double-quote character; "
    "for emphasis or quoting a word use single quotes or « » instead. "
    "Apostrophes in contractions (it's, don't, Aries's) are fine as-is — do not escape or remove them. "
    "Example of a correctly formatted value: {{\"intro\": \"Aries is often called the zodiac's 'trailblazer'.\"}} "
    "Write with confidence and finality — never think out loud or self-correct inside the "
    "text (no phrases like 'wait, actually' or 'let me correct that' or 'hold on'). "
    "For any section about famous or notable people, name exactly 3-4 real people with one "
    "short sentence each, without discussing or second-guessing their birth dates or signs."
)

_JSON_SCHEMA = (
    "Return JSON: {{\"intro\": \"...\", \"sections\": [{{\"title\": \"...\", \"text\": \"...\"}}], "
    "\"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}], \"cta_text\": \"...\"}}"
)

PROMPTS_I18N = {
    "zodiac": (
        "Write a detailed profile of the zodiac sign {name} ({dates}, element {element}, ruling planet {ruler}). "
        "Include sections: 1) Personality overview, 2) Strengths, 3) Weaknesses, "
        "4) Love and relationships, 5) Career, 6) Compatibility with other signs, "
        "7) Health and wellbeing, 8) Money and finances, 9) Famous {name} people, 10) Advice. "
        "Create 5 FAQ with answers. " + _QUALITY_I18N + _JSON_SCHEMA
    ),
    "tarot": (
        "Write the detailed meaning of the Tarot card \"{name}\". "
        "Include sections: 1) Upright meaning, 2) Reversed meaning, "
        "3) In love and relationships, 4) In career and finances, 5) The card's advice, 6) Combinations with other cards. "
        "Create 5 FAQ. " + _QUALITY_I18N + _JSON_SCHEMA
    ),
    "rune": (
        "Write the detailed meaning of the rune {name} ({symbol}). "
        "Include sections: 1) Origin and etymology, 2) Magical meaning, "
        "3) Upright meaning in divination, 4) Reversed meaning in divination, "
        "5) Use in bind runes and runic scripts, 6) The rune as an amulet. "
        "Create 5 FAQ. " + _QUALITY_I18N + _JSON_SCHEMA
    ),
    "numerology": (
        "Write the detailed meaning of life path number {number} — \"{name}\". "
        "Include sections: 1) Character and personality, 2) Life purpose, "
        "3) Career and vocation, 4) Love and relationships, 5) Health, "
        "6) Famous people with this number. "
        "Create 5 FAQ. " + _QUALITY_I18N + _JSON_SCHEMA
    ),
}

# ru entry is the previously hardcoded system message, unchanged.
SYSTEM_GEN = {
    "ru": "Ты SEO-копирайтер для эзотерического сайта Mystral. Пиши на русском. Отвечай строго JSON. Никаких иероглифов или символов других алфавитов.",
    "en": "You are an SEO copywriter for the esoteric platform Mystral. Write in English. Respond strictly with JSON. No characters from other scripts.",
    "es": "You are an SEO copywriter for the esoteric platform Mystral. Write in Spanish. Respond strictly with JSON. No characters from other scripts.",
    "pt": "You are an SEO copywriter for the esoteric platform Mystral. Write in Brazilian Portuguese. Respond strictly with JSON. No characters from other scripts.",
    "tr": "You are an SEO copywriter for the esoteric platform Mystral. Write in Turkish. Respond strictly with JSON. No characters from other scripts.",
    "uk": "You are an SEO copywriter for the esoteric platform Mystral. Write in Ukrainian. Respond strictly with JSON. No characters from other scripts.",
}

_FALLBACK_TEXTS = {
    "ru": ("Подробная информация скоро появится. Зарегистрируйтесь в Mystral для персонального анализа.",
           "Описание", "Контент генерируется. Пожалуйста, зайдите позже.",
           "Как узнать больше?", "Зарегистрируйтесь в Mystral для персонального анализа.",
           "Откройте Mystral для персонального эзотерического анализа."),
    "en": ("Detailed content is coming soon. Sign up on Mystral for a personal analysis.",
           "Description", "This content is being generated. Please check back later.",
           "How can I learn more?", "Sign up on Mystral for a personal analysis.",
           "Discover Mystral for a personal esoteric analysis."),
    "es": ("La información detallada estará disponible pronto. Regístrate en Mystral para un análisis personal.",
           "Descripción", "El contenido se está generando. Vuelve más tarde, por favor.",
           "¿Cómo puedo saber más?", "Regístrate en Mystral para un análisis personal.",
           "Descubre Mystral para un análisis esotérico personal."),
    "pt": ("As informações detalhadas estarão disponíveis em breve. Cadastre-se no Mystral para uma análise pessoal.",
           "Descrição", "O conteúdo está sendo gerado. Volte mais tarde, por favor.",
           "Como saber mais?", "Cadastre-se no Mystral para uma análise pessoal.",
           "Descubra o Mystral para uma análise esotérica pessoal."),
    "tr": ("Ayrıntılı içerik yakında burada olacak. Kişisel analiz için Mystral'a kaydolun.",
           "Açıklama", "İçerik oluşturuluyor. Lütfen daha sonra tekrar deneyin.",
           "Daha fazlasını nasıl öğrenebilirim?", "Kişisel analiz için Mystral'a kaydolun.",
           "Kişisel ezoterik analiz için Mystral'ı keşfedin."),
    "uk": ("Детальна інформація незабаром з'явиться. Зареєструйтеся в Mystral для персонального аналізу.",
           "Опис", "Контент генерується. Будь ласка, завітайте пізніше.",
           "Як дізнатися більше?", "Зареєструйтеся в Mystral для персонального аналізу.",
           "Відкрийте Mystral для персонального езотеричного аналізу."),
}


def _fallback(lang: str) -> dict:
    intro, sec_title, sec_text, faq_q, faq_a, cta = _FALLBACK_TEXTS.get(lang, _FALLBACK_TEXTS["ru"])
    return {
        "intro": intro,
        "sections": [{"title": sec_title, "text": sec_text}],
        "faq": [{"q": faq_q, "a": faq_a}],
        "cta_text": cta,
        "_fallback": True,  # never persisted; template switches robots to noindex
    }


def _build_prompt(page_type: str, data: dict, lang: str) -> str | None:
    if lang == "ru":
        tpl = PROMPTS.get(page_type, "")
        return tpl.format(**data) if tpl else None
    tpl = PROMPTS_I18N.get(page_type, "")
    if not tpl:
        return None
    return tpl.format(language=_LANG_NAME[lang], **data)


# TZ-060 follow-up #3: 6144 ALSO truncated a clean response (Capricorn/en —
# intro + 10 sections + 4 of 5 faq, cut off with finish_reason=length,
# confirmed via the explicit signal added in follow-up #2, not guesswork).
# A tokenizer-based estimate from a similar prior response (cl100k_base as
# a proxy for DeepSeek's real tokenizer) predicted ~3-4.5k tokens would be
# enough — it was wrong; proxy-tokenizer math is not reliable here, so stop
# incrementally chasing the real number. max_tokens is a ceiling, not a
# cost — pages that finish in fewer tokens aren't affected either way, and
# every provider behind this model supports >=16k output. Jump straight to
# a generous cap instead of nudging it up again next time this recurs.
GENERATION_MAX_TOKENS = 12000

_REQUIRED_KEYS = ("intro", "sections", "faq", "cta_text")


def _parse_content_json(raw: str, page_type: str, slug: str, lang: str) -> dict | None:
    """Extracts and parses the JSON object from a model response. Tries
    strict json.loads first, then json_repair as a fallback for the class of
    error seen in production ("Expecting ',' delimiter" from an unescaped
    literal quote inside a string value) — but ALWAYS validates the result
    has the expected shape before trusting it, since json_repair silently
    returns '' on unrecoverable garbage instead of raising. Returns None (and
    logs) on any failure — callers must never mistake None for content."""
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if not (start >= 0 and end > start):
        logger.error("SEO gen for %s/%s/%s: no JSON object found in response (len=%d): %r",
                     page_type, slug, lang, len(raw), raw[:200])
        return None

    candidate = raw[start:end]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as e:
        logger.warning("SEO gen for %s/%s/%s: strict JSON parse failed (%s), trying json_repair", page_type, slug, lang, e)
        try:
            parsed = json_repair.loads(candidate)
        except Exception as repair_err:
            logger.error("SEO gen for %s/%s/%s: json_repair raised: %s", page_type, slug, lang, repair_err)
            return None
        if not isinstance(parsed, dict) or not all(k in parsed for k in _REQUIRED_KEYS):
            logger.error("SEO gen for %s/%s/%s: json_repair produced an invalid/incomplete result: %r",
                         page_type, slug, lang, parsed)
            return None
        logger.info("SEO gen for %s/%s/%s: recovered via json_repair", page_type, slug, lang)

    if not isinstance(parsed, dict) or not all(k in parsed for k in _REQUIRED_KEYS):
        logger.error("SEO gen for %s/%s/%s: parsed JSON missing required keys: %r",
                     page_type, slug, lang, parsed if isinstance(parsed, dict) else type(parsed))
        return None
    return parsed


async def _generate_and_store(page_type: str, slug: str, data: dict, session: AsyncSession, lang: str) -> dict:
    """Calls the LLM, persists the result, returns parsed content (or an
    in-memory fallback on any failure — fallbacks are never persisted)."""
    prompt = _build_prompt(page_type, data, lang)
    if not prompt:
        return _fallback(lang)

    try:
        from app.core.groq_client import _get_async_client
        from app.core.prompts import LANG_ENFORCE
        client = _get_async_client()
        resp = await client.chat.completions.create(
            model="deepseek/deepseek-v4-flash",
            messages=[
                {"role": "system", "content": SYSTEM_GEN.get(lang, SYSTEM_GEN["en"]) + LANG_ENFORCE.get(lang, "")},
                {"role": "user", "content": prompt},
            ],
            max_tokens=GENERATION_MAX_TOKENS,
            temperature=0.7,
            # TZ-060: forces syntactically valid JSON at the API level
            # (confirmed supported by deepseek-v4-flash's OpenRouter provider
            # pool) instead of relying on the model's free-text escaping —
            # root fix for the "Expecting ',' delimiter" parse failures.
            response_format={"type": "json_object"},
        )
        finish_reason = getattr(resp.choices[0], "finish_reason", None)
        if finish_reason == "length":
            # Definitive signal (not a guess from char offsets): the model
            # hit max_tokens mid-response, so the JSON is genuinely
            # incomplete — no amount of json_repair fixes a response that
            # was never finished. Surfacing this distinctly from other
            # parse failures says whether GENERATION_MAX_TOKENS needs to go
            # up again, vs. an unrelated model formatting slip.
            logger.warning("SEO gen for %s/%s/%s: response truncated by max_tokens (finish_reason=length)",
                           page_type, slug, lang)
        raw = _CLEAN_RE.sub('', resp.choices[0].message.content or "")
        parsed = _parse_content_json(raw, page_type, slug, lang)
        if parsed is None:
            return _fallback(lang)
    except Exception as e:
        logger.error("SEO gen error for %s/%s/%s: %s", page_type, slug, lang, e)
        return _fallback(lang)

    # TZ-073: this persistence step used to sit outside any try/except, so a
    # transient DB failure here (pool exhaustion, dropped connection, etc.)
    # propagated as an unhandled 500 to the caller — even though the LLM had
    # already produced valid content. Serve the real content regardless of
    # whether caching it succeeds; a page must never 500 just because its
    # cache write failed (it will simply regenerate next request).
    try:
        content_str = json.dumps(parsed, ensure_ascii=False)
        result = await session.exec(
            select(SeoContent).where(
                SeoContent.page_type == page_type, SeoContent.slug == slug, SeoContent.lang == lang,
            )
        )
        cached = result.first()
        if cached:
            cached.content = content_str
            cached.generated_at = datetime.utcnow()
            session.add(cached)
        else:
            session.add(SeoContent(page_type=page_type, slug=slug, lang=lang, content=content_str))
        await session.commit()
        logger.info("Generated SEO content for %s/%s/%s", page_type, slug, lang)
    except Exception as e:
        logger.error("SEO gen for %s/%s/%s: failed to persist generated content, serving it unpersisted: %s",
                     page_type, slug, lang, e)
    return parsed


# Fire-and-forget refresh tasks: keep references so they aren't GC'd,
# and dedupe so a burst of requests on one stale page spawns one refresh.
_bg_tasks: set = set()
_refreshing: set = set()


async def _refresh_content(page_type: str, slug: str, data: dict, lang: str) -> None:
    from app.core.database import get_session_context
    key = (page_type, slug, lang)
    try:
        async with get_session_context() as session:
            await _generate_and_store(page_type, slug, data, session, lang)
    except Exception as e:
        logger.error("SEO SWR refresh failed for %s/%s/%s: %s", page_type, slug, lang, e)
    finally:
        _refreshing.discard(key)


def _spawn_refresh(page_type: str, slug: str, data: dict, lang: str) -> None:
    key = (page_type, slug, lang)
    if key in _refreshing:
        return
    _refreshing.add(key)
    task = asyncio.create_task(_refresh_content(page_type, slug, data, lang))
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


async def get_seo_content(page_type: str, slug: str, data: dict, session: AsyncSession, lang: str = "ru") -> dict:
    """Cached content for one page+language. `data` must already be localized
    for `lang` (see seo_i18n.localize_*). Expired rows are served stale and
    refreshed in the background so crawlers never wait on generation; only a
    complete cache miss generates synchronously."""
    # TZ-082: this lookup used to sit outside any try/except, unlike the
    # read+write pair in _generate_and_store's persistence step below (fixed
    # in TZ-073 for the exact same failure class) — a transient DB hiccup
    # here (pool exhaustion, dropped connection) propagated as an unhandled
    # 500 instead of just falling through to on-demand generation. This is
    # the one call site TZ-073 missed, and the reason its 21-page fingerprint
    # (12 runes + all 9 numerology — the only pages whose on-demand path
    # holds a connection open across a live LLM call, per TZ-073's notes)
    # came back.
    cached = None
    try:
        result = await session.exec(
            select(SeoContent).where(
                SeoContent.page_type == page_type, SeoContent.slug == slug, SeoContent.lang == lang,
            )
        )
        cached = result.first()
    except Exception as e:
        logger.error("SEO cache lookup failed for %s/%s/%s: %s, generating fresh", page_type, slug, lang, e)
        # On Postgres, a failed statement leaves the session's transaction
        # aborted — any further use (including _generate_and_store's own
        # persistence step below, on this same session) raises
        # InFailedSQLTransactionError until rolled back. Without this, the
        # page would still render (TZ-073's guard catches that too) but the
        # freshly generated content would never make it into the cache for
        # this request, confirmed against real Postgres.
        try:
            await session.rollback()
        except Exception:
            pass

    if cached and cached.generated_at:
        try:
            parsed = json.loads(cached.content)
        except Exception:
            parsed = None
        if parsed is not None:
            if cached.generated_at <= datetime.utcnow() - timedelta(days=30):
                logger.debug("Stale cache for %s/%s/%s — serving stale, refreshing in background", page_type, slug, lang)
                _spawn_refresh(page_type, slug, data, lang)
            return parsed

    return await _generate_and_store(page_type, slug, data, session, lang)


def localize_data(page_type: str, data: dict, lang: str) -> dict:
    """Localized copy of a seo_data entry for prompt building (used by the
    warm cache and the batch script; page handlers localize via seo_i18n
    directly). Tarot gets a target-language "name" key for the i18n prompt."""
    if lang == "ru":
        return data
    from app.data.seo_i18n import localize_num, localize_rune, localize_sign, tarot_display_name
    if page_type == "zodiac":
        return localize_sign(data, lang)
    if page_type == "tarot":
        return {**data, "name": tarot_display_name(data, lang)}
    if page_type == "rune":
        return localize_rune(data, lang)
    if page_type == "numerology":
        return localize_num(data, lang)
    return data


def seo_page_items() -> list[tuple[str, str, dict]]:
    """(page_type, slug, raw ru data) for all 123 individual SEO pages."""
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
    return items


async def warm_seo_cache() -> None:
    from app.core.database import get_session_context
    from app.data.seo_i18n import ALL_LANGS

    langs = [l.strip() for l in settings.seo_warm_langs.split(",") if l.strip() in ALL_LANGS]
    items = seo_page_items()
    total = len(items) * len(langs)
    logger.info("SEO cache warm: starting %d pages (langs: %s)", total, ",".join(langs))

    # TZ-074: errors used to be counted globally, so 3 failures anywhere (e.g.
    # all rune pages hitting a transient issue) aborted the *entire* warm —
    # including zodiac/tarot/numerology types that were working fine. Track
    # consecutive errors per page_type instead: once a type trips 3 in a row,
    # skip only its remaining slugs (still checking cache first, since earlier
    # slugs of that type may already be warm) and keep warming the other types.
    consecutive_errors: dict[str, int] = {}
    skipped_types: set[tuple[str, str]] = set()
    failed: list[str] = []
    done = 0
    for lang in langs:
        consecutive_errors.clear()
        for ptype, slug, data in items:
            done += 1
            async with get_session_context() as session:
                result = await session.exec(
                    select(SeoContent).where(
                        SeoContent.page_type == ptype, SeoContent.slug == slug, SeoContent.lang == lang,
                    )
                )
                if result.first():
                    continue
                if (lang, ptype) in skipped_types:
                    failed.append(f"{ptype}/{slug}/{lang} (skipped: repeated errors for this type)")
                    continue
                try:
                    await get_seo_content(ptype, slug, localize_data(ptype, data, lang), session, lang)
                    logger.info("SEO cache warm: %s/%s/%s (%d/%d)", ptype, slug, lang, done, total)
                    consecutive_errors[ptype] = 0
                except Exception as e:
                    logger.error("SEO warm error %s/%s/%s: %s", ptype, slug, lang, e)
                    failed.append(f"{ptype}/{slug}/{lang}")
                    consecutive_errors[ptype] = consecutive_errors.get(ptype, 0) + 1
                    if consecutive_errors[ptype] >= 3:
                        logger.warning(
                            "SEO cache warm: 3 consecutive errors for type=%s lang=%s, skipping its remaining slugs (other types continue)",
                            ptype, lang,
                        )
                        skipped_types.add((lang, ptype))
            await asyncio.sleep(3)

    if failed:
        logger.warning("SEO cache warm: %d/%d pages did not warm: %s", len(failed), total, ", ".join(failed))
    logger.info("SEO cache warm: done")
