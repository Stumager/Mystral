"""TZ-115: Денежная линия.

REFERENCE_DATE is not invented — it's a date independently confirmed by
brute-force simulation (TZ-115 step 0, see PROGRESS.md) to reproduce the
worked example matrica-sudby.ru's own money-line diagram shows (entry=12,
source=9, block=21), read directly off two diagram images on that page
(not through a text summariser, which fabricated a different, nonexistent
formula on a different competitor page during this same investigation —
see the money_line.py module docstring). Of the 504 calendar dates whose
(core, ancestry) match that example's (8, 19), 420 (83%) share this exact
date's realization value (4) — no other of the nine points comes close —
which is what pins the third input to `realization` rather than any other
point, and this test locks that result in against future drift.
"""
from datetime import date
from unittest.mock import patch
from uuid import uuid4

from app.data.destiny_matrix import calculate
from app.data.money_line import MONEY_ENERGY, MONEY_LINE_POSITIONS, build_money_line, calculate_money_line
from tests.conftest import make_user
from tests.test_matrix import FIXTURE_BIRTH

REFERENCE_DATE = date(1909, 1, 11)
REFERENCE_RESULT = {"entry": 12, "source": 9, "block": 21}

# FIXTURE_BIRTH = date(1995, 11, 8); core=5, ancestry=6, realization=7
# (see test_matrix.FIXTURE_POINTS): entry=reduce22(5+7)=12,
# source=reduce22(5+6)=11, block=reduce22(12+11)=reduce22(23)=5.
FIXTURE_MONEY_LINE = {"entry": 12, "source": 11, "block": 5}


def _fake_stream(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        yield "data: [DONE]\n\n"
    return _gen()


class TestCalculateMoneyLine:
    def test_matches_the_diagram_example(self):
        points = calculate(REFERENCE_DATE)
        assert points["core"] == 8 and points["ancestry"] == 19 and points["realization"] == 4
        assert calculate_money_line(points) == REFERENCE_RESULT

    def test_fixture_birth(self):
        assert calculate_money_line(calculate(FIXTURE_BIRTH)) == FIXTURE_MONEY_LINE

    def test_entry_equals_the_karmic_tails_first_digit(self):
        """The money-line entry point is defined as reduce22(core+realization)
        — the same value as karmic_tail.calculate_tail()'s t1, which is the
        numeric backing for matrica-sudby.ru's own claim that the entry
        energy 'sits on the karmic tail too'."""
        from app.data.karmic_tail import calculate_tail
        for birth in (REFERENCE_DATE, FIXTURE_BIRTH, date(2000, 1, 1)):
            points = calculate(birth)
            t1, _, _ = calculate_tail(points)
            assert calculate_money_line(points)["entry"] == t1, birth

    def test_all_positions_land_in_arcana_range(self):
        for birth in (REFERENCE_DATE, FIXTURE_BIRTH, date(1975, 8, 29), date(2000, 1, 1)):
            for n in calculate_money_line(calculate(birth)).values():
                assert 1 <= n <= 22

    def test_every_energy_has_original_ru_en_text(self):
        assert len(MONEY_ENERGY) == 22
        for n, entry in MONEY_ENERGY.items():
            for field in ("flow", "block"):
                assert entry[f"{field}_ru"], n
                assert entry[f"{field}_en"], n

    def test_no_fatalistic_or_blame_framing(self):
        """Content-safety guard (see module docstring): matrica-sudby.ru's
        own money-line text frames blocked money as a karmic punishment a
        person may be powerless to fix ("karmic ban", "always negative",
        past-life guilt causing this life's money to be taken away) —
        reviewed with the product owner and deliberately kept out of
        MONEY_ENERGY. This locks that decision in against a future edit
        (by a person or an AI-generation pass) accidentally reintroducing
        it."""
        banned_ru = (
            "карм", "провал", "наказан", "проклят", "обречен", "обречён",
            "невозможно", "никогда не", "не сможет",
        )
        banned_en = (
            "karma", "curse", "cursed", "doom", "punish", "impossible",
            "never will", "won't ever",
        )
        for n, entry in MONEY_ENERGY.items():
            for field in ("flow_ru", "block_ru"):
                low = entry[field].lower()
                assert not any(w in low for w in banned_ru), (n, field, entry[field])
            for field in ("flow_en", "block_en"):
                low = entry[field].lower()
                assert not any(w in low for w in banned_en), (n, field, entry[field])


class TestBuildMoneyLine:
    def test_payload_shape(self):
        result = build_money_line(FIXTURE_BIRTH, "ru")
        by_id = {p["id"]: p for p in result["positions"]}
        assert set(by_id) == set(MONEY_LINE_POSITIONS)
        for pos, expected in FIXTURE_MONEY_LINE.items():
            assert by_id[pos]["arcana"] == expected
            assert by_id[pos]["flow"] and by_id[pos]["block"]

    def test_localises(self):
        ru = build_money_line(FIXTURE_BIRTH, "ru")
        en = build_money_line(FIXTURE_BIRTH, "en")
        ru_entry = next(p for p in ru["positions"] if p["id"] == "entry")
        en_entry = next(p for p in en["positions"] if p["id"] == "entry")
        assert ru_entry["arcana"] == en_entry["arcana"]
        assert ru_entry["flow"] != en_entry["flow"]


class TestMoneyLineEndpoint:
    async def test_free_user_is_paywalled(self, client, auth_headers):
        res = await client.get("/v1/matrix/money-line", headers=auth_headers)
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_the_money_line(self, client, pro_headers):
        res = await client.get("/v1/matrix/money-line", headers=pro_headers)
        assert res.status_code == 200
        body = res.json()
        by_id = {p["id"]: p["arcana"] for p in body["positions"]}
        assert by_id == FIXTURE_MONEY_LINE
        assert body["birth_date"] == FIXTURE_BIRTH.isoformat()

    async def test_requires_a_birth_date(self, client):
        _, headers = await make_user(email=f"nobd-{uuid4()}@test.com", with_profile=False, tier="pro")
        res = await client.get("/v1/matrix/money-line", headers=headers)
        assert res.status_code == 400

    async def test_requires_auth(self, client):
        assert (await client.get("/v1/matrix/money-line")).status_code in (401, 403)


class TestMoneyLineInterpretAccess:
    async def test_free_user_is_paywalled(self, client, auth_headers):
        res = await client.post("/v1/matrix/money-line/interpret", headers=auth_headers, json={"lang": "ru"})
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_a_stream(self, client, pro_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream):
            res = await client.post("/v1/matrix/money-line/interpret", headers=pro_headers, json={"lang": "ru"})
        assert res.status_code == 200
        assert "reading" in res.text

    async def test_requires_auth(self, client):
        res = await client.post("/v1/matrix/money-line/interpret", json={"lang": "ru"})
        assert res.status_code in (401, 403)


class TestMoneyLineInterpretPrompt:
    async def _capture(self, client, headers, lang="ru"):
        captured = {}

        def _capturing_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            captured["messages"] = messages
            return _fake_stream(messages, max_tokens, lang, on_finish)

        with patch("app.core.cached_stream.safe_groq_stream", _capturing_stream):
            await client.post("/v1/matrix/money-line/interpret", headers=headers, json={"lang": lang})
        return captured["messages"][-1]["content"]

    async def test_prompt_carries_all_three_positions(self, client, pro_headers):
        prompt = await self._capture(client, pro_headers)
        for n in FIXTURE_MONEY_LINE.values():
            assert str(n) in prompt

    async def test_prompt_localises(self, client, pro_headers):
        prompt = await self._capture(client, pro_headers, lang="en")
        assert "money flow" in prompt or "Income source" in prompt
