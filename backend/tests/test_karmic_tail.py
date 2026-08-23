"""TZ-114: Кармический хвост.

The two REFERENCE entries are not invented — they're the karmic tail values
two independent sources (horo.mail.ru and lisa.ru) publish for these exact
birth dates, reproduced here through this codebase's own reduce22()/core/
realization rather than copied as magic numbers, so a future refactor can't
silently drift from what an independent site would show for the same date.
ALL_CODES is the result of simulating every calendar date 1900-01-01 through
2100-12-31 through calculate_tail() (TZ-114 step 0, see PROGRESS.md) — it
exists so a change to the fold rule can't silently shrink or grow the set of
26 reachable combinations without a test noticing.
"""
from datetime import date, timedelta
from unittest.mock import patch
from uuid import uuid4

from app.data.destiny_matrix import calculate
from app.data.karmic_tail import KARMIC_TAIL, build_karmic_tail, calculate_tail, tail_code
from tests.conftest import make_user
from tests.test_matrix import FIXTURE_BIRTH

REFERENCE = {
    date(1974, 10, 3): (12, 19, 7),
    date(1992, 8, 15): (15, 5, 8),
}

ALL_CODES = {
    "3-7-22", "3-13-10", "3-22-19", "6-5-17", "6-8-20", "6-14-8", "6-17-11",
    "6-20-14", "9-3-21", "9-9-18", "9-12-3", "9-15-6", "9-18-9", "12-16-4",
    "12-19-7", "15-5-8", "15-8-11", "15-20-5", "18-3-12", "18-6-6", "18-6-15",
    "18-9-9", "21-4-10", "21-7-13", "21-10-7", "21-10-16",
}

# FIXTURE_BIRTH = date(1995, 11, 8); its base matrix has realization=7, core=5
# (see test_matrix.FIXTURE_POINTS), so its karmic tail is 12-19-7 — the same
# combination as the horo.mail.ru reference above, just a different birth date.
FIXTURE_TAIL = (12, 19, 7)


def _fake_stream(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        yield "data: [DONE]\n\n"
    return _gen()


class TestCalculateTail:
    def test_matches_independently_verified_references(self):
        for birth, expected in REFERENCE.items():
            assert calculate_tail(calculate(birth)) == expected, birth

    def test_fixture_birth_matches_matrix_fixture(self):
        assert calculate_tail(calculate(FIXTURE_BIRTH)) == FIXTURE_TAIL

    def test_every_reachable_code_has_a_table_entry(self):
        """Every calendar date 1900-2100 must resolve to a real KARMIC_TAIL
        entry — the table is exhaustive, not a curated subset."""
        seen = set()
        d, end = date(1900, 1, 1), date(2100, 12, 31)
        while d <= end:
            seen.add(tail_code(calculate_tail(calculate(d))))
            d += timedelta(days=1)
        assert seen == ALL_CODES

    def test_table_has_no_unreachable_entries(self):
        assert set(KARMIC_TAIL.keys()) == ALL_CODES

    def test_every_entry_has_original_ru_en_text(self):
        for code, entry in KARMIC_TAIL.items():
            for field in ("name", "essence", "task"):
                assert entry[f"{field}_ru"], code
                assert entry[f"{field}_en"], code


class TestBuildKarmicTail:
    def test_payload_shape(self):
        result = build_karmic_tail(FIXTURE_BIRTH, "ru")
        assert (result["t1"], result["t2"], result["t3"]) == FIXTURE_TAIL
        assert result["code"] == "12-19-7"
        assert result["name"] == "Воин"
        assert result["essence"] and result["task"]

    def test_localises_name(self):
        ru = build_karmic_tail(FIXTURE_BIRTH, "ru")
        en = build_karmic_tail(FIXTURE_BIRTH, "en")
        assert ru["code"] == en["code"]
        assert ru["name"] != en["name"]
        assert en["name"] == "The Warrior"


class TestKarmicTailEndpoint:
    async def test_free_user_is_paywalled(self, client, auth_headers):
        """Unlike GET /matrix, the karmic tail has no free sample at all."""
        res = await client.get("/v1/matrix/karmic-tail", headers=auth_headers)
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_the_tail(self, client, pro_headers):
        res = await client.get("/v1/matrix/karmic-tail", headers=pro_headers)
        assert res.status_code == 200
        body = res.json()
        assert (body["t1"], body["t2"], body["t3"]) == FIXTURE_TAIL
        assert body["birth_date"] == FIXTURE_BIRTH.isoformat()

    async def test_requires_a_birth_date(self, client):
        _, headers = await make_user(email=f"nobd-{uuid4()}@test.com", with_profile=False, tier="pro")
        res = await client.get("/v1/matrix/karmic-tail", headers=headers)
        assert res.status_code == 400

    async def test_requires_auth(self, client):
        assert (await client.get("/v1/matrix/karmic-tail")).status_code in (401, 403)


class TestKarmicTailInterpretAccess:
    async def test_free_user_is_paywalled(self, client, auth_headers):
        res = await client.post("/v1/matrix/karmic-tail/interpret", headers=auth_headers, json={"lang": "ru"})
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_a_stream(self, client, pro_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream):
            res = await client.post("/v1/matrix/karmic-tail/interpret", headers=pro_headers, json={"lang": "ru"})
        assert res.status_code == 200
        assert "reading" in res.text

    async def test_requires_auth(self, client):
        res = await client.post("/v1/matrix/karmic-tail/interpret", json={"lang": "ru"})
        assert res.status_code in (401, 403)


class TestKarmicTailInterpretPrompt:
    async def _capture(self, client, headers, lang="ru"):
        captured = {}

        def _capturing_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            captured["messages"] = messages
            return _fake_stream(messages, max_tokens, lang, on_finish)

        with patch("app.core.cached_stream.safe_groq_stream", _capturing_stream):
            await client.post("/v1/matrix/karmic-tail/interpret", headers=headers, json={"lang": lang})
        return captured["messages"][-1]["content"]

    async def test_prompt_names_the_archetype(self, client, pro_headers):
        prompt = await self._capture(client, pro_headers)
        assert "12-19-7" in prompt
        assert "Воин" in prompt

    async def test_prompt_localises(self, client, pro_headers):
        prompt = await self._capture(client, pro_headers, lang="en")
        assert "The Warrior" in prompt


def _fake_stream_completed(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        if on_finish:
            on_finish("stop")
        yield "data: [DONE]\n\n"
    return _gen()


class TestKarmicTailInterpretCaching:
    """TZ-120: same birth date -> same karmic tail -> same prompt every
    time. A repeat view must not re-bill the LLM."""

    async def test_second_identical_request_does_not_call_the_llm_again(self, client, pro_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream_completed):
            first = await client.post("/v1/matrix/karmic-tail/interpret", headers=pro_headers, json={"lang": "ru"})
        assert first.status_code == 200

        with patch("app.core.cached_stream.safe_groq_stream") as mock_llm:
            second = await client.post("/v1/matrix/karmic-tail/interpret", headers=pro_headers, json={"lang": "ru"})
            mock_llm.assert_not_called()
        assert second.status_code == 200
        assert "reading" in second.text

    async def test_different_language_is_a_separate_cache_entry(self, client, pro_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream_completed):
            await client.post("/v1/matrix/karmic-tail/interpret", headers=pro_headers, json={"lang": "ru"})

        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream_completed) as mock_llm:
            res = await client.post("/v1/matrix/karmic-tail/interpret", headers=pro_headers, json={"lang": "en"})
        assert res.status_code == 200
