"""TZ-097: a free-text follow-up question on an already-interpreted tarot
reading. Pro-only, capped at MAX_CLARIFICATIONS_PER_READING per reading (not
per hour, so it can't become an unbounded AI chat on one reading), and the
question length is capped up front (QA-030 precedent) rather than waiting
for a dedicated bug report about it.
"""
import json
from unittest.mock import patch
from uuid import uuid4

from app.api.v1.tarot import MAX_CLARIFICATIONS_PER_READING
from app.core.database import AsyncSessionLocal
from app.models.user import TarotClarification


async def _fake_stream(*a, **k):
    yield 'data: {"text": "Answer "}\n\n'
    yield 'data: {"text": "text"}\n\n'
    yield "data: [DONE]\n\n"


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


async def _draw_and_interpret(client, headers, spread_id="three_cards"):
    draw = await client.post("/v1/tarot/spread", headers=headers, json={"spread_id": spread_id, "lang": "ru"})
    reading_id = draw.json()["reading_id"]
    cards = draw.json()["cards"]
    with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
        await client.post("/v1/tarot/interpret", headers=headers, json={
            "spread_id": spread_id, "cards": cards, "positions": [], "lang": "ru", "reading_id": reading_id,
        })
    return reading_id


class TestTarotClarifyAccessControl:
    async def test_free_user_gets_paywall(self, client, auth_headers):
        res = await client.post("/v1/tarot/clarify", headers=auth_headers, json={
            "reading_id": str(uuid4()), "question": "What about my career?", "lang": "ru",
        })
        assert res.status_code == 402
        assert res.json()["message"] == "FREE_LIMIT_REACHED"

    async def test_reading_not_owned_by_user_404(self, client, pro_headers, auth_headers):
        reading_id = await _draw_and_interpret(client, auth_headers)
        res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
            "reading_id": reading_id, "question": "What about my career?", "lang": "ru",
        })
        assert res.status_code == 404

    async def test_unknown_reading_id_404(self, client, pro_headers):
        res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
            "reading_id": str(uuid4()), "question": "What about my career?", "lang": "ru",
        })
        assert res.status_code == 404

    async def test_no_interpretation_yet_rejected(self, client, pro_headers):
        draw = await client.post("/v1/tarot/spread", headers=pro_headers, json={"spread_id": "three_cards", "lang": "ru"})
        res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
            "reading_id": draw.json()["reading_id"], "question": "What about my career?", "lang": "ru",
        })
        assert res.status_code == 400


class TestTarotClarifyValidation:
    async def test_empty_question_rejected(self, client, pro_headers):
        reading_id = await _draw_and_interpret(client, pro_headers)
        res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
            "reading_id": reading_id, "question": "", "lang": "ru",
        })
        assert res.status_code == 422

    async def test_oversized_question_rejected(self, client, pro_headers):
        reading_id = await _draw_and_interpret(client, pro_headers)
        res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
            "reading_id": reading_id, "question": "A" * 501, "lang": "ru",
        })
        assert res.status_code == 422

    async def test_max_length_question_accepted(self, client, pro_headers):
        reading_id = await _draw_and_interpret(client, pro_headers)
        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
            res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                "reading_id": reading_id, "question": "A" * 500, "lang": "ru",
            })
        assert res.status_code == 200


class TestTarotClarifyGeneration:
    async def test_successful_clarify_streams_answer(self, client, pro_headers):
        reading_id = await _draw_and_interpret(client, pro_headers)
        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
            res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                "reading_id": reading_id, "question": "What about my career?", "lang": "ru",
            })
        assert res.status_code == 200
        assert _extract_sse_text(res.text) == "Answer text"

    async def test_answer_persisted_to_same_reading(self, client, pro_headers):
        reading_id = await _draw_and_interpret(client, pro_headers)
        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
            await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                "reading_id": reading_id, "question": "What about my career?", "lang": "ru",
            })
        async with AsyncSessionLocal() as s:
            from sqlmodel import select
            rows = (await s.exec(select(TarotClarification).where(
                TarotClarification.reading_id == __import__("uuid").UUID(reading_id)
            ))).all()
        assert len(rows) == 1
        assert rows[0].question == "What about my career?"
        assert rows[0].answer == "Answer text"
        assert rows[0].lang == "ru"

    async def test_prompt_includes_original_interpretation_context(self, client, pro_headers):
        """The clarify prompt must build on the reading already given, not
        start over from nothing."""
        reading_id = await _draw_and_interpret(client, pro_headers)
        captured = {}

        async def _capturing_stream(messages, **kwargs):
            captured["messages"] = messages
            async for chunk in _fake_stream():
                yield chunk

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_capturing_stream):
            await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                "reading_id": reading_id, "question": "What about my career?", "lang": "ru",
            })
        user_msg = captured["messages"][1]["content"]
        assert "Hello world" not in user_msg  # sanity: not the fake interpret text by accident
        assert "What about my career?" in user_msg


class TestTarotClarifyPerReadingLimit:
    async def test_limit_enforced(self, client, pro_headers):
        reading_id = await _draw_and_interpret(client, pro_headers)
        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
            for _ in range(MAX_CLARIFICATIONS_PER_READING):
                res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                    "reading_id": reading_id, "question": "Tell me more?", "lang": "ru",
                })
                assert res.status_code == 200

            over_limit = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                "reading_id": reading_id, "question": "One more?", "lang": "ru",
            })
        assert over_limit.status_code == 429
        assert over_limit.json()["error"] == "clarify_limit"

    async def test_limit_is_per_reading_not_global(self, client, pro_headers):
        reading_a = await _draw_and_interpret(client, pro_headers)
        reading_b = await _draw_and_interpret(client, pro_headers)
        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=_fake_stream):
            for _ in range(MAX_CLARIFICATIONS_PER_READING):
                await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                    "reading_id": reading_a, "question": "Tell me more?", "lang": "ru",
                })
            # reading_a is now at its cap, but reading_b is untouched
            res = await client.post("/v1/tarot/clarify", headers=pro_headers, json={
                "reading_id": reading_b, "question": "Tell me more?", "lang": "ru",
            })
        assert res.status_code == 200
