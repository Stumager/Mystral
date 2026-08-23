"""TZ-091: TZ-089 fixed this exact bug for /numerology/interpret alone (see
test_numerology_security.py); this extends the same fix to the other 7
AI-interpret endpoints. Each returns a StreamingResponse while depending —
directly via its own `Depends(get_session)`, or indirectly through
get_current_user's own `Depends(get_session)` — on a pooled DB session.
FastAPI/Starlette don't run a dependency's cleanup until the *entire* ASGI
response (including the SSE body) has been sent, so without an explicit
early `await session.close()` the pooled connection sits checked-out for as
long as the LLM stream takes. Under a burst of back-to-back requests this
was observed taking 13.88s-48.42s across 6 calls, with the 6th never
responding (pool exhaustion). Each affected endpoint now closes its session
right after its last DB read, before building/returning the
StreamingResponse.

These tests prove the ordering directly: AsyncSession.close is wrapped to
record when it runs, and safe_groq_stream is patched so the fake
generator's first line checks whether close already happened. Without the
fix, close() only runs after the whole stream is drained — i.e. after these
assertions — so this test fails against unpatched code and passes once each
endpoint closes its session early.
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from sqlmodel.ext.asyncio.session import AsyncSession

import pytest

from app.core.database import AsyncSessionLocal
from app.models.user import UserPartner


@pytest.fixture
def close_tracker():
    """Wrap AsyncSession.close so tests can observe *when* it runs relative
    to the streaming generator starting, without touching production code."""
    state = {"closed": False}
    orig_close = AsyncSession.close

    async def _tracking_close(self):
        state["closed"] = True
        return await orig_close(self)

    with patch.object(AsyncSession, "close", _tracking_close):
        yield state


def _fake_stream_factory(state):
    async def _fake_stream(messages, max_tokens=900, lang="ru", on_finish=None):
        state["closed_when_stream_started"] = state["closed"]
        yield 'data: {"text": "ok"}\n\n'
        if on_finish:
            on_finish("stop")
        yield "data: [DONE]\n\n"
    return _fake_stream


async def _make_partner(user_id, birth_date=date(1992, 7, 10)):
    async with AsyncSessionLocal() as session:
        partner = UserPartner(user_id=user_id, label="Partner", birth_date=birth_date)
        session.add(partner)
        await session.commit()
        await session.refresh(partner)
        return partner


class TestNumerologyInterpretClosesSessionBeforeStreaming:
    async def test_core_section(self, client, auth_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.numerology.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/numerology/interpret",
                headers=auth_headers,
                json={"section": "core", "lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestTarotInterpretClosesSessionBeforeStreaming:
    async def test_interpret(self, client, auth_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.tarot.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/tarot/interpret",
                headers=auth_headers,
                json={
                    "spread_id": "card_of_day",
                    "cards": [{"id": 0, "name_display": "The Fool", "reversed": False}],
                    "positions": ["Today"],
                    "lang": "ru",
                },
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestTarotClarifyClosesSessionBeforeStreaming:
    async def test_clarify(self, client, pro_headers, close_tracker):
        draw = await client.post("/v1/tarot/spread", headers=pro_headers,
                                  json={"spread_id": "three_cards", "lang": "ru"})
        reading_id = draw.json()["reading_id"]

        async def _fake_interpret_stream(*a, **k):
            yield 'data: {"text": "Base interpretation"}\n\n'
            yield "data: [DONE]\n\n"

        with patch("app.api.v1.tarot.safe_groq_stream", _fake_interpret_stream):
            await client.post("/v1/tarot/interpret", headers=pro_headers, json={
                "spread_id": "three_cards", "cards": draw.json()["cards"], "positions": [],
                "lang": "ru", "reading_id": reading_id,
            })

        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.tarot.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/tarot/clarify",
                headers=pro_headers,
                json={"reading_id": reading_id, "question": "What about my career?", "lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestRunesInterpretClosesSessionBeforeStreaming:
    async def test_interpret(self, client, auth_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.runes.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/runes/interpret",
                headers=auth_headers,
                json={
                    "spread_type": "rune_of_day",
                    "drawn_runes": [{"id": "fehu", "name": "Fehu", "reversed": False, "position_name": "Today"}],
                    "lang": "ru",
                },
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestHoroscopeStreamClosesSessionBeforeStreaming:
    async def test_stream(self, client, auth_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.horoscope.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/horoscope/stream",
                headers=auth_headers,
                json={"sign": "aries", "lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestLunarAiRecommendClosesSessionBeforeStreaming:
    async def test_ai_recommend(self, client, pro_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.lunar.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/lunar/ai-recommend",
                headers=pro_headers,
                json={"lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestCompatibilityInterpretClosesSessionBeforeStreaming:
    async def test_interpret_signs(self, client, auth_headers, auth_user, close_tracker):
        user, _ = auth_user
        partner = await _make_partner(user.id)

        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.compatibility.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/compatibility/interpret",
                headers=auth_headers,
                json={"compat_type": "signs", "partner_id": str(partner.id), "score": 80, "lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestNatalInterpretClosesSessionBeforeStreaming:
    async def test_interpret(self, client, auth_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        empty_chart = {
            "planets": [], "ascendant": {}, "houses": [],
            "aspects": [], "extra_points": [], "stelliums": [],
        }
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value=empty_chart), \
             patch("app.api.v1.natal.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/natal/interpret",
                headers=auth_headers,
                json={
                    "name": "Test", "year": 1995, "month": 11, "day": 8,
                    "city": "Moscow", "section": "personality", "lang": "ru",
                },
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestMatrixInterpretClosesSessionBeforeStreaming:
    """TZ-101 — the 10th streaming endpoint. Pro-only, so this runs on
    pro_headers; the profile read it needs happens before the close."""

    async def test_interpret(self, client, pro_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.matrix.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/matrix/interpret",
                headers=pro_headers,
                json={"point": "core", "lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestKarmicTailInterpretClosesSessionBeforeStreaming:
    """TZ-114 — the 11th streaming endpoint, same module as matrix.py's
    /matrix/interpret above. Pro-only, so this runs on pro_headers."""

    async def test_interpret(self, client, pro_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.matrix.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/matrix/karmic-tail/interpret",
                headers=pro_headers,
                json={"lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestMoneyLineInterpretClosesSessionBeforeStreaming:
    """TZ-115 — the 12th streaming endpoint, same module as matrix.py's
    /matrix/interpret above. Pro-only, so this runs on pro_headers."""

    async def test_interpret(self, client, pro_headers, close_tracker):
        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.matrix.safe_groq_stream", fake_stream):
            res = await client.post(
                "/v1/matrix/money-line/interpret",
                headers=pro_headers,
                json={"lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestChildrenMatrixInterpretClosesSessionBeforeStreaming:
    """TZ-116 — the 13th streaming endpoint, same module as matrix.py's
    /matrix/interpret above. Pro-only, so this runs on pro_headers."""

    async def test_interpret(self, client, pro_headers, close_tracker):
        created = await client.post("/v1/children", headers=pro_headers,
                                    json={"name": "Kid", "birth_date": "2018-05-01"})
        child_id = created.json()["id"]

        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.matrix.safe_groq_stream", fake_stream):
            res = await client.post(
                f"/v1/matrix/child/{child_id}/interpret",
                headers=pro_headers,
                json={"point": "core", "lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True


class TestMatrixCompatibilityInterpretClosesSessionBeforeStreaming:
    """TZ-118 — the 14th streaming endpoint, same module as matrix.py's
    /matrix/interpret above. Pro-only, so this runs on pro_headers. Reuses
    the existing UserPartner (task 4's finding), not a new model."""

    async def test_interpret(self, client, pro_headers, pro_user, close_tracker):
        user, _ = pro_user
        partner = await _make_partner(user.id)

        fake_stream = _fake_stream_factory(close_tracker)
        with patch("app.api.v1.matrix.safe_groq_stream", fake_stream):
            res = await client.post(
                f"/v1/matrix/compatibility/{partner.id}/interpret",
                headers=pro_headers,
                json={"lang": "ru"},
            )
        assert res.status_code == 200
        assert close_tracker["closed_when_stream_started"] is True
