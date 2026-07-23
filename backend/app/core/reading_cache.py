"""TZ-092: caches a generated AI interpretation to the (reading_id, lang)
that produced it, so a persisted tarot/rune reading (TZ-092/QA-003's
day/year read-back) shows the same interpretation on every re-view instead
of re-billing OpenRouter and risking different wording for "the same" card.
Same compound-key cache pattern as seo_generator.get_seo_content's
(page_type, slug, lang) — simpler here since a reading's interpretation has
no staleness concept: once generated for a (reading_id, lang), it's correct
forever (the reading itself never changes).
"""
import logging
from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import ReadingInterpretation

logger = logging.getLogger(__name__)


async def get_cached_interpretation(
    session: AsyncSession, reading_id: UUID, reading_type: str, lang: str
) -> Optional[str]:
    """Existing interpretation text for this (reading_id, lang), or None on
    a genuine miss or a lookup failure (fails open to normal generation)."""
    try:
        result = await session.exec(
            select(ReadingInterpretation).where(
                ReadingInterpretation.reading_id == reading_id,
                ReadingInterpretation.reading_type == reading_type,
                ReadingInterpretation.lang == lang,
            )
        )
        row = result.first()
        return row.text if row else None
    except Exception as e:
        logger.warning("Interpretation cache lookup failed for %s/%s/%s: %s", reading_type, reading_id, lang, e)
        return None


async def store_interpretation(reading_id: UUID, reading_type: str, lang: str, text: str) -> None:
    """Called after the SSE stream has already finished, on its own
    short-lived session — the request's own session was released early
    (TZ-089/091: a pooled connection must not sit checked out for the
    LLM call's duration), so there's nothing to reuse here."""
    try:
        async with AsyncSessionLocal() as session:
            session.add(ReadingInterpretation(
                reading_id=reading_id, reading_type=reading_type, lang=lang, text=text,
            ))
            await session.commit()
    except Exception as e:
        logger.warning("Failed to store interpretation for %s/%s/%s: %s", reading_type, reading_id, lang, e)
