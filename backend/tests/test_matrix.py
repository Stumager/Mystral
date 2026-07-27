"""TZ-101: Матрица судьбы.

The reference matrices in TestMatrixCalculation are not invented — they're
the values an independent live calculator returned for these four dates
during the pre-implementation formula check (TZ-101 step 0, recorded in
PROGRESS.md). They exist so that a future refactor of reduce22() or the
point wiring can't silently drift away from what users will see when they
cross-check us against another site. The dates were picked to cover the
cases that actually distinguish the competing formula variants: a day > 22,
a point landing exactly on 22, and a date where "digit-sum the whole date"
and "sum the three arcana" disagree.
"""
from datetime import date
from unittest.mock import patch
from uuid import uuid4

from app.data.destiny_matrix import (
    POINT_IDS,
    ancestral_centre,
    arcana_name,
    calculate,
    reduce22,
)
from tests.conftest import make_user

# Order matches POINT_IDS: personality, talents, ancestry, realization, core,
# father_gift, mother_gift, father_task, mother_task.
REFERENCE = {
    date(1990, 5, 15): [15, 5, 19, 12, 6, 20, 6, 4, 9],
    date(1975, 8, 29): [11, 8, 22, 5, 10, 19, 3, 9, 16],
    date(1987, 12, 3): [3, 12, 7, 22, 8, 15, 19, 11, 7],
    date(2000, 1, 1): [1, 1, 2, 4, 8, 2, 3, 6, 5],
}

# The conftest profile fixture's birth date.
FIXTURE_BIRTH = date(1995, 11, 8)
FIXTURE_POINTS = [8, 11, 6, 7, 5, 19, 17, 13, 15]


def _fake_stream(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        yield "data: [DONE]\n\n"
    return _gen()


class TestReduce22:
    def test_leaves_range_untouched(self):
        for n in range(1, 23):
            assert reduce22(n) == n

    def test_folds_by_digit_sum_not_subtraction(self):
        # 29 -> 2+9 = 11, not 29-22 = 7. Both rules circulate online; the
        # digit-sum one is what the sources we verified against use.
        assert reduce22(29) == 11
        assert reduce22(47) == 11
        assert reduce22(1990) == 19

    def test_does_not_preserve_pythagorean_master_numbers(self):
        # app.data.numerology.reduce() would stop at 11/22/33 as master
        # numbers; here they're ordinary arcana and 33 must keep folding.
        assert reduce22(33) == 6


class TestArcanaNames:
    def test_fool_is_twenty_two_not_zero(self):
        assert arcana_name(22, "en") == "The Fool"
        assert arcana_name(1, "en") == "The Magician"
        assert arcana_name(21, "en") == "The World"

    def test_every_arcana_resolves_in_every_language(self):
        for lang in ("ru", "en", "es", "pt", "tr", "uk"):
            for n in range(1, 23):
                assert arcana_name(n, lang)


class TestMatrixCalculation:
    def test_matches_independently_verified_references(self):
        for birth, expected in REFERENCE.items():
            values = calculate(birth)
            assert [values[p] for p in POINT_IDS] == expected, birth

    def test_all_points_land_in_arcana_range(self):
        for birth in REFERENCE:
            for n in calculate(birth).values():
                assert 1 <= n <= 22

    def test_ancestral_corners_derive_from_adjacent_personal_points(self):
        v = calculate(date(1990, 5, 15))
        assert v["father_gift"] == reduce22(v["personality"] + v["talents"])
        assert v["mother_gift"] == reduce22(v["talents"] + v["ancestry"])
        assert v["father_task"] == reduce22(v["ancestry"] + v["realization"])
        assert v["mother_task"] == reduce22(v["realization"] + v["personality"])

    def test_ancestral_centre_sums_the_four_corners(self):
        v = calculate(date(1990, 5, 15))
        assert ancestral_centre(v) == reduce22(
            v["father_gift"] + v["mother_gift"] + v["father_task"] + v["mother_task"]
        )

    def test_leap_day_and_century_boundaries(self):
        for birth in (date(2000, 2, 29), date(1900, 1, 31), date(2024, 12, 31)):
            values = calculate(birth)
            assert len(values) == 9
            assert all(1 <= n <= 22 for n in values.values())


class TestMatrixEndpoint:
    async def test_free_user_gets_the_full_matrix(self, client, auth_headers):
        """The access model splits at interpretation, not at calculation —
        the octagram itself is free, like the natal wheel."""
        res = await client.get("/v1/matrix", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert [p["arcana"] for p in body["points"]] == FIXTURE_POINTS
        assert body["birth_date"] == FIXTURE_BIRTH.isoformat()

    async def test_returns_nine_points_with_position_and_square(self, client, auth_headers):
        body = (await client.get("/v1/matrix", headers=auth_headers)).json()
        assert [p["id"] for p in body["points"]] == POINT_IDS
        assert len(body["points"]) == 9
        assert sum(1 for p in body["points"] if p["square"] == "personal") == 5
        assert sum(1 for p in body["points"] if p["square"] == "ancestral") == 4
        assert len({p["pos"] for p in body["points"]}) == 9
        for p in body["points"]:
            assert p["arcana_name"] and p["light"] and p["shadow"]

    async def test_localises_arcana_names(self, client, auth_headers):
        ru = (await client.get("/v1/matrix?lang=ru", headers=auth_headers)).json()
        en = (await client.get("/v1/matrix?lang=en", headers=auth_headers)).json()
        assert [p["arcana"] for p in ru["points"]] == [p["arcana"] for p in en["points"]]
        assert ru["points"][0]["arcana_name"] != en["points"][0]["arcana_name"]

    async def test_requires_a_birth_date(self, client):
        _, headers = await make_user(email=f"nobd-{uuid4()}@test.com", with_profile=False)
        res = await client.get("/v1/matrix", headers=headers)
        assert res.status_code == 400

    async def test_requires_auth(self, client):
        assert (await client.get("/v1/matrix")).status_code in (401, 403)


class TestMatrixInterpretAccess:
    async def test_free_user_is_paywalled(self, client, auth_headers):
        res = await client.post("/v1/matrix/interpret", headers=auth_headers,
                                json={"point": "core", "lang": "ru"})
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_free_user_is_paywalled_on_every_point(self, client, auth_headers):
        """No point is a free sample — the confirmed model gates all of them."""
        for point in POINT_IDS:
            res = await client.post("/v1/matrix/interpret", headers=auth_headers,
                                    json={"point": point, "lang": "ru"})
            assert res.status_code == 402, point

    async def test_pro_user_gets_a_stream(self, client, pro_headers):
        with patch("app.api.v1.matrix.safe_groq_stream", _fake_stream):
            res = await client.post("/v1/matrix/interpret", headers=pro_headers,
                                    json={"point": "core", "lang": "ru"})
        assert res.status_code == 200
        assert "reading" in res.text

    async def test_unknown_point_is_rejected(self, client, pro_headers):
        res = await client.post("/v1/matrix/interpret", headers=pro_headers,
                                json={"point": "not_a_point", "lang": "ru"})
        assert res.status_code == 422

    async def test_requires_auth(self, client):
        res = await client.post("/v1/matrix/interpret", json={"point": "core"})
        assert res.status_code in (401, 403)


class TestMatrixInterpretPrompt:
    async def _capture(self, client, headers, point, lang="ru"):
        captured = {}

        def _capturing_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            captured["messages"] = messages
            return _fake_stream(messages, max_tokens, lang, on_finish)

        with patch("app.api.v1.matrix.safe_groq_stream", _capturing_stream):
            await client.post("/v1/matrix/interpret", headers=headers,
                              json={"point": point, "lang": lang})
        return captured["messages"][-1]["content"]

    async def test_prompt_carries_the_whole_octagram(self, client, pro_headers):
        """A point reads differently depending on its neighbours, so the
        surrounding matrix has to reach the model, not just the one arcana."""
        prompt = await self._capture(client, pro_headers, "core")
        for n in FIXTURE_POINTS:
            assert str(n) in prompt

    async def test_prompt_names_the_requested_point(self, client, pro_headers):
        prompt = await self._capture(client, pro_headers, "father_task")
        assert arcana_name(FIXTURE_POINTS[POINT_IDS.index("father_task")], "ru") in prompt

    async def test_prompt_asks_for_both_light_and_shadow(self, client, pro_headers):
        prompt = await self._capture(client, pro_headers, "personality")
        assert "плюсе" in prompt and "теневом" in prompt
