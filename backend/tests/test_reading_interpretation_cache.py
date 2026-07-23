"""TZ-092: a tarot/rune reading's interpretation used to be regenerated on
every view — extra billed OpenRouter calls for the exact same persisted
reading (TZ-092/QA-003 made the reading itself, but not its interpretation,
stable for the period), and the wording could differ between "the same"
card's re-views. Interpretations are now cached to (reading_id, lang), same
compound-key pattern as seo_generator.get_seo_content's (page_type, slug,
lang): a hit replays the stored text without touching the LLM; a miss
generates once and stores it.
"""
import json

from app.core.database import AsyncSessionLocal
from app.models.user import ReadingInterpretation


def _extract_sse_text(body: str) -> str:
    out = ""
    for line in body.split("\n"):
        if not line.startswith("data: "):
            continue
        data = line[6:].strip()
        if data == "[DONE]":
            break
        try:
            out += json.loads(data).get("text", "")
        except Exception:
            pass
    return out


async def _fake_stream(*a, **k):
    yield 'data: {"text": "Hello "}\n\n'
    yield 'data: {"text": "world"}\n\n'
    yield "data: [DONE]\n\n"


class TestTarotInterpretationCache:
    async def test_repeat_request_same_reading_returns_identical_text_without_new_llm_call(self, client, pro_headers):
        from unittest.mock import patch

        draw = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
        reading_id = draw.json()["reading_id"]
        cards = draw.json()["cards"]

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            first = await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": cards, "positions": [], "lang": "ru", "reading_id": reading_id,
            })
            second = await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": cards, "positions": [], "lang": "ru", "reading_id": reading_id,
            })

        assert mock_stream.call_count == 1, "second request must not call the LLM again"
        text1 = _extract_sse_text(first.text)
        text2 = _extract_sse_text(second.text)
        assert text1 == "Hello world"
        assert text2 == text1

    async def test_new_reading_id_generates_fresh(self, client, pro_headers):
        from unittest.mock import patch

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            d1 = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": d1.json()["cards"], "positions": [], "lang": "ru",
                "reading_id": d1.json()["reading_id"],
            })
            d2 = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": d2.json()["cards"], "positions": [], "lang": "ru",
                "reading_id": d2.json()["reading_id"],
            })

        assert d1.json()["reading_id"] != d2.json()["reading_id"]
        assert mock_stream.call_count == 2

    async def test_same_reading_new_language_generates_fresh(self, client, pro_headers):
        from unittest.mock import patch

        draw = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
        reading_id = draw.json()["reading_id"]
        cards = draw.json()["cards"]

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": cards, "positions": [], "lang": "ru", "reading_id": reading_id,
            })
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": cards, "positions": [], "lang": "en", "reading_id": reading_id,
            })

        assert mock_stream.call_count == 2

    async def test_no_reading_id_always_generates(self, client, pro_headers):
        from unittest.mock import patch

        draw = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
        cards = draw.json()["cards"]

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": cards, "positions": [], "lang": "ru",
            })
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": cards, "positions": [], "lang": "ru",
            })

        assert mock_stream.call_count == 2

    async def test_cache_row_persisted_with_correct_type_and_lang(self, client, pro_headers):
        from unittest.mock import patch

        draw = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
        reading_id = draw.json()["reading_id"]

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": draw.json()["cards"], "positions": [], "lang": "ru",
                "reading_id": reading_id,
            })

        async with AsyncSessionLocal() as s:
            from sqlmodel import select
            rows = (await s.exec(select(ReadingInterpretation).where(
                ReadingInterpretation.reading_id == __import__("uuid").UUID(reading_id)
            ))).all()
        assert len(rows) == 1
        assert rows[0].reading_type == "tarot"
        assert rows[0].lang == "ru"
        assert rows[0].text == "Hello world"


class TestRunesInterpretationCache:
    async def test_repeat_request_same_reading_returns_identical_text_without_new_llm_call(self, client, pro_headers):
        from unittest.mock import patch

        draw = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "three_norns", "lang": "ru"})
        reading_id = draw.json()["reading_id"]
        runes = draw.json()["drawn_runes"]

        with patch("app.api.v1.runes.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            first = await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": runes, "lang": "ru", "reading_id": reading_id,
            })
            second = await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": runes, "lang": "ru", "reading_id": reading_id,
            })

        assert mock_stream.call_count == 1
        assert _extract_sse_text(first.text) == "Hello world"
        assert _extract_sse_text(second.text) == "Hello world"

    async def test_new_reading_id_generates_fresh(self, client, pro_headers):
        from unittest.mock import patch

        with patch("app.api.v1.runes.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            d1 = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "three_norns", "lang": "ru"})
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": d1.json()["drawn_runes"], "lang": "ru",
                "reading_id": d1.json()["reading_id"],
            })
            d2 = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "three_norns", "lang": "ru"})
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": d2.json()["drawn_runes"], "lang": "ru",
                "reading_id": d2.json()["reading_id"],
            })

        assert d1.json()["reading_id"] != d2.json()["reading_id"]
        assert mock_stream.call_count == 2

    async def test_same_reading_new_language_generates_fresh(self, client, pro_headers):
        from unittest.mock import patch

        draw = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "three_norns", "lang": "ru"})
        reading_id = draw.json()["reading_id"]
        runes = draw.json()["drawn_runes"]

        with patch("app.api.v1.runes.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": runes, "lang": "ru", "reading_id": reading_id,
            })
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": runes, "lang": "en", "reading_id": reading_id,
            })

        assert mock_stream.call_count == 2

    async def test_no_reading_id_always_generates(self, client, pro_headers):
        """Covers the personal-rune AI path, which calls /runes/interpret
        with no drawn reading behind it at all."""
        from unittest.mock import patch

        draw = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "three_norns", "lang": "ru"})
        runes = draw.json()["drawn_runes"]

        with patch("app.api.v1.runes.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": runes, "lang": "ru",
            })
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "three_norns", "drawn_runes": runes, "lang": "ru",
            })

        assert mock_stream.call_count == 2

    async def test_period_spread_reentry_reuses_cached_interpretation(self, client, pro_headers):
        """End-to-end with the TZ-092/QA-003 persistence: re-entering rune of
        the day returns the same reading_id, and interpreting it twice must
        still only call the LLM once."""
        from unittest.mock import patch

        d1 = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "rune_of_day", "lang": "ru"})
        d2 = await client.post("/v1/runes/draw", headers=pro_headers, json={"spread_type": "rune_of_day", "lang": "ru"})
        assert d1.json()["reading_id"] == d2.json()["reading_id"]

        with patch("app.api.v1.runes.safe_groq_stream", side_effect=_fake_stream) as mock_stream:
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "rune_of_day", "drawn_runes": d1.json()["drawn_runes"], "lang": "ru",
                "reading_id": d1.json()["reading_id"],
            })
            await client.post("/v1/runes/interpret", headers=pro_headers, json={
                "spread_type": "rune_of_day", "drawn_runes": d2.json()["drawn_runes"], "lang": "ru",
                "reading_id": d2.json()["reading_id"],
            })

        assert mock_stream.call_count == 1
