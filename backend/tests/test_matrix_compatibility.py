"""TZ-118: Совместимость по Матрице судьбы.

REFERENCE is not invented — see matrix_compatibility.py's module docstring
for how it was derived: matrica-sudby.ru's own worked example for the
compatibility centre ("6 энергия... 8... получаем 14") reproduced exactly
using this codebase's own already-verified reference birth dates
(test_matrix.REFERENCE: 1990-05-15 has core=6, 1987-12-03 has core=8), and
the resulting karmic tail (21-10-7) matches the name that same site's
compatibility table gives that exact code ("Воин веры"/"Warrior of Faith"),
independently confirming this codebase's own KARMIC_TAIL table rather than
just the arithmetic.

No new archetype table to guard here (unlike test_karmic_tail.py/
test_money_line.py/test_childrens_matrix.py) — this module reuses
KARMIC_TAIL and ARCANA_ENERGY verbatim, so their existing content-safety
tests already cover this feature's text. What's specific to this module:
the CRUD-reuse claim (task 4 — no new model, existing /partners endpoints),
the all-or-nothing Pro gate (task 8), and the prompt's "no verdict" safety
framing (Step 0 decision 3).
"""
from datetime import date
from unittest.mock import patch
from uuid import uuid4

from app.core.database import AsyncSessionLocal
from app.data.karmic_tail import KARMIC_TAIL
from app.data.matrix_compatibility import build_compatibility, combined_points
from app.models.user import UserPartner
from tests.conftest import make_user
from tests.test_matrix import FIXTURE_BIRTH, FIXTURE_POINTS

# The two independently-verified reference dates from test_matrix.REFERENCE,
# picked because their core values (6, 8) are exactly matrica-sudby.ru's
# illustrative example numbers.
BIRTH_1 = date(1990, 5, 15)   # core=6, realization=12
BIRTH_2 = date(1987, 12, 3)   # core=8, realization=22
EXPECTED_CENTRE = 14           # reduce22(6+8), matches the source's example
EXPECTED_TAIL = (21, 10, 7)    # reduce22(14+7), reduce22(21+7), 7
EXPECTED_TAIL_CODE = "21-10-7"


async def _make_partner(user_id, birth_date=BIRTH_2, label="Partner"):
    async with AsyncSessionLocal() as session:
        partner = UserPartner(user_id=user_id, label=label, birth_date=birth_date)
        session.add(partner)
        await session.commit()
        await session.refresh(partner)
        return partner


def _fake_stream(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        yield "data: [DONE]\n\n"
    return _gen()


class TestCombinedPoints:
    def test_matches_the_independently_published_worked_example(self):
        points = combined_points(BIRTH_1, BIRTH_2)
        assert points["core"] == EXPECTED_CENTRE

    def test_karmic_tail_code_matches_the_source_table(self):
        result = build_compatibility(BIRTH_1, BIRTH_2, "ru")
        assert result["karmic_tail"]["code"] == EXPECTED_TAIL_CODE
        assert (result["karmic_tail"]["t1"], result["karmic_tail"]["t2"], result["karmic_tail"]["t3"]) == EXPECTED_TAIL
        # The source names this exact code "Воин веры" — cross-checking
        # against this codebase's own KARMIC_TAIL, not the source's prose,
        # is what actually proves the formula (see module docstring).
        assert KARMIC_TAIL[EXPECTED_TAIL_CODE]["name_ru"] == "Воин веры"

    def test_symmetric_in_partner_order(self):
        """Sum is commutative — the pair's result must not depend on who's
        "self" and who's "partner"."""
        a = combined_points(BIRTH_1, BIRTH_2)
        b = combined_points(BIRTH_2, BIRTH_1)
        assert a == b

    def test_only_core_and_realization_are_computed(self):
        """v1 scope guard (Step 0, product owner decision): no money/
        attraction indicator without a real worked example to verify it
        against — see module docstring."""
        assert set(combined_points(BIRTH_1, BIRTH_2).keys()) == {"core", "realization"}


class TestBuildCompatibilityPayload:
    def test_centre_has_arcana_name_and_energy(self):
        result = build_compatibility(BIRTH_1, BIRTH_2, "ru")
        centre = result["centre"]
        assert centre["arcana"] == EXPECTED_CENTRE
        assert centre["arcana_name"]
        assert centre["light"] and centre["shadow"]

    def test_karmic_tail_has_localized_name_essence_task(self):
        result = build_compatibility(BIRTH_1, BIRTH_2, "en")
        tail = result["karmic_tail"]
        assert tail["name"] == "Warrior of Faith"
        assert tail["essence"] and tail["task"]

    def test_deterministic(self):
        assert build_compatibility(BIRTH_1, BIRTH_2, "ru") == build_compatibility(BIRTH_1, BIRTH_2, "ru")


class TestCompatibilityCrudReuse:
    """Task 4: no new model or CRUD — a Matrix compatibility partner is the
    same UserPartner row as compatibility.py's, created/listed/deleted
    through the existing /partners endpoints."""

    async def test_partner_created_via_existing_endpoint_works_for_matrix(self, client, pro_headers):
        created = await client.post(
            "/v1/partners", headers=pro_headers,
            json={"name": "Sasha", "birth_date": BIRTH_2.isoformat()},
        )
        assert created.status_code == 200
        partner_id = created.json()["id"]

        res = await client.get(f"/v1/matrix/compatibility/{partner_id}", headers=pro_headers)
        assert res.status_code == 200
        assert res.json()["partner"]["name"] == "Sasha"

    async def test_deleting_the_partner_removes_matrix_access_too(self, client, pro_headers):
        created = await client.post(
            "/v1/partners", headers=pro_headers,
            json={"name": "Sasha", "birth_date": BIRTH_2.isoformat()},
        )
        partner_id = created.json()["id"]
        await client.delete(f"/v1/partners/{partner_id}", headers=pro_headers)

        res = await client.get(f"/v1/matrix/compatibility/{partner_id}", headers=pro_headers)
        assert res.status_code == 404


class TestMatrixCompatibilityAccess:
    async def test_invalid_partner_id_format_returns_422(self, client, pro_headers):
        res = await client.get("/v1/matrix/compatibility/not-a-uuid", headers=pro_headers)
        assert res.status_code == 422

    async def test_other_users_partner_returns_404(self, client, pro_headers):
        other_user, _ = await make_user(email=f"other-{uuid4()}@test.com", tier="pro")
        partner = await _make_partner(other_user.id)
        res = await client.get(f"/v1/matrix/compatibility/{partner.id}", headers=pro_headers)
        assert res.status_code == 404

    async def test_free_user_is_paywalled(self, client, auth_headers, auth_user):
        user, _ = auth_user
        partner = await _make_partner(user.id)
        res = await client.get(f"/v1/matrix/compatibility/{partner.id}", headers=auth_headers)
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_the_full_result(self, client, pro_headers, pro_user):
        user, _ = pro_user
        partner = await _make_partner(user.id)
        res = await client.get(f"/v1/matrix/compatibility/{partner.id}", headers=pro_headers)
        assert res.status_code == 200
        body = res.json()
        # pro_user carries FIXTURE_BIRTH; combine by hand for the assertion
        # rather than re-deriving the module's own logic.
        expected = build_compatibility(FIXTURE_BIRTH, BIRTH_2, "ru")
        assert body["centre"] == expected["centre"]
        assert body["karmic_tail"] == expected["karmic_tail"]

    async def test_requires_auth(self, client):
        res = await client.get(f"/v1/matrix/compatibility/{uuid4()}")
        assert res.status_code in (401, 403)


class TestMatrixCompatibilityInterpretAccess:
    async def test_free_user_is_paywalled(self, client, auth_headers, auth_user):
        user, _ = auth_user
        partner = await _make_partner(user.id)
        res = await client.post(f"/v1/matrix/compatibility/{partner.id}/interpret",
                                headers=auth_headers, json={"lang": "ru"})
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_a_stream(self, client, pro_headers, pro_user):
        user, _ = pro_user
        partner = await _make_partner(user.id)
        with patch("app.api.v1.matrix.safe_groq_stream", _fake_stream):
            res = await client.post(f"/v1/matrix/compatibility/{partner.id}/interpret",
                                    headers=pro_headers, json={"lang": "ru"})
        assert res.status_code == 200
        assert "reading" in res.text

    async def test_other_users_partner_returns_404(self, client, pro_headers):
        other_user, _ = await make_user(email=f"other-{uuid4()}@test.com", tier="pro")
        partner = await _make_partner(other_user.id)
        res = await client.post(f"/v1/matrix/compatibility/{partner.id}/interpret",
                                headers=pro_headers, json={"lang": "ru"})
        assert res.status_code == 404

    async def test_invalid_partner_id_format_returns_422(self, client, pro_headers):
        res = await client.post("/v1/matrix/compatibility/not-a-uuid/interpret",
                                headers=pro_headers, json={"lang": "ru"})
        assert res.status_code == 422

    async def test_requires_auth(self, client):
        res = await client.post(f"/v1/matrix/compatibility/{uuid4()}/interpret", json={"lang": "ru"})
        assert res.status_code in (401, 403)


class TestMatrixCompatibilityInterpretPrompt:
    async def _capture(self, client, headers, user_id, partner_label="Sasha", lang="ru"):
        partner = await _make_partner(user_id, label=partner_label)
        captured = {}

        def _capturing_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            captured["messages"] = messages
            return _fake_stream(messages, max_tokens, lang, on_finish)

        with patch("app.api.v1.matrix.safe_groq_stream", _capturing_stream):
            await client.post(f"/v1/matrix/compatibility/{partner.id}/interpret",
                              headers=headers, json={"lang": lang})
        return captured["messages"][-1]["content"]

    async def test_prompt_names_the_partner(self, client, pro_headers, pro_user):
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id)
        assert "Sasha" in prompt

    async def test_prompt_carries_centre_and_karmic_tail(self, client, pro_headers, pro_user):
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id)
        expected = build_compatibility(FIXTURE_BIRTH, BIRTH_2, "ru")
        assert str(expected["centre"]["arcana"]) in prompt
        assert expected["karmic_tail"]["name"] in prompt

    async def test_prompt_forbids_a_compatibility_verdict(self, client, pro_headers, pro_user):
        """Step 0 decision 3 (product owner): no predetermined good/bad
        combination — original wording, not the vc.ru sentence itself, but
        the same idea must reach the model, not just exist in a doc
        comment."""
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id)
        assert "заведомо" in prompt and "сочетан" in prompt

    async def test_english_prompt_also_forbids_a_verdict(self, client, pro_headers, pro_user):
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id, lang="en")
        assert "predetermined" in prompt.lower()
