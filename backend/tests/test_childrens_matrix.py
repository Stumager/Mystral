"""TZ-116: Детская матрица.

No new calculation to verify (see childrens_matrix.py's module docstring) —
these tests cover the CRUD/ownership pattern mirrored from compatibility.py's
UserPartner tests, the free/Pro point-level gating (unlike TZ-114/115's
all-or-nothing gate), and the content-safety guard against fatalistic
capability labels the product owner asked to be locked in, not just noted.
"""
from datetime import date
from unittest.mock import patch
from uuid import uuid4

from app.data.childrens_matrix import CHILD_ARCANA_ENERGY, FREE_POINT_ID
from app.data.destiny_matrix import POINT_IDS, calculate
from app.core.database import AsyncSessionLocal
from app.models.user import UserChild
from tests.conftest import make_user
from tests.test_matrix import FIXTURE_BIRTH, FIXTURE_POINTS


async def _make_child(user_id, birth_date=FIXTURE_BIRTH, label="Kid"):
    async with AsyncSessionLocal() as session:
        child = UserChild(user_id=user_id, label=label, birth_date=birth_date)
        session.add(child)
        await session.commit()
        await session.refresh(child)
        return child


def _fake_stream(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        yield "data: [DONE]\n\n"
    return _gen()


class TestChildCrud:
    async def test_create_list_delete(self, client, auth_headers):
        res = await client.post("/v1/children", headers=auth_headers,
                                json={"name": "Kid", "birth_date": "2018-05-01"})
        assert res.status_code == 200
        child_id = res.json()["id"]

        listed = await client.get("/v1/children", headers=auth_headers)
        assert listed.status_code == 200
        assert any(c["id"] == child_id and c["name"] == "Kid" for c in listed.json())

        deleted = await client.delete(f"/v1/children/{child_id}", headers=auth_headers)
        assert deleted.status_code == 200
        listed_after = await client.get("/v1/children", headers=auth_headers)
        assert not any(c["id"] == child_id for c in listed_after.json())

    async def test_create_requires_name(self, client, auth_headers):
        res = await client.post("/v1/children", headers=auth_headers,
                                json={"name": "", "birth_date": "2018-05-01"})
        assert res.status_code == 422

    async def test_invalid_child_id_format_returns_422(self, client, auth_headers):
        res = await client.get("/v1/matrix/child/not-a-uuid", headers=auth_headers)
        assert res.status_code == 422

    async def test_other_users_child_returns_404(self, client, auth_headers):
        other_user, _ = await make_user(email=f"other-{uuid4()}@test.com", tier="pro")
        child = await _make_child(other_user.id)
        res = await client.get(f"/v1/matrix/child/{child.id}", headers=auth_headers)
        assert res.status_code == 404

    async def test_requires_auth(self, client):
        assert (await client.get("/v1/children")).status_code in (401, 403)


class TestChildMatrixAccess:
    async def test_free_user_sees_only_the_free_point(self, client, auth_headers, auth_user):
        user, _ = auth_user
        child = await _make_child(user.id)
        res = await client.get(f"/v1/matrix/child/{child.id}", headers=auth_headers)
        assert res.status_code == 200
        by_id = {p["id"]: p for p in res.json()["points"]}
        assert by_id[FREE_POINT_ID]["locked"] is False
        assert by_id[FREE_POINT_ID]["arcana"] == FIXTURE_POINTS[POINT_IDS.index(FREE_POINT_ID)]
        assert by_id[FREE_POINT_ID]["strength"]
        for pid in POINT_IDS:
            if pid == FREE_POINT_ID:
                continue
            assert by_id[pid]["locked"] is True, pid
            assert by_id[pid]["arcana"] is None, pid
            assert by_id[pid]["strength"] is None, pid

    async def test_pro_user_sees_all_nine_points(self, client, pro_headers, pro_user):
        user, _ = pro_user
        child = await _make_child(user.id)
        res = await client.get(f"/v1/matrix/child/{child.id}", headers=pro_headers)
        assert res.status_code == 200
        by_id = {p["id"]: p for p in res.json()["points"]}
        assert [by_id[pid]["arcana"] for pid in POINT_IDS] == FIXTURE_POINTS
        for pid in POINT_IDS:
            assert by_id[pid]["locked"] is False
            assert by_id[pid]["strength"] and by_id[pid]["support"]

    async def test_child_payload_includes_name_and_birth_date(self, client, auth_headers, auth_user):
        user, _ = auth_user
        child = await _make_child(user.id, label="Alex")
        res = await client.get(f"/v1/matrix/child/{child.id}", headers=auth_headers)
        body = res.json()
        assert body["child"]["name"] == "Alex"
        assert body["child"]["birth_date"] == FIXTURE_BIRTH.isoformat()


class TestChildMatrixInterpretAccess:
    async def test_free_user_is_paywalled_even_on_the_free_point(self, client, auth_headers, auth_user):
        user, _ = auth_user
        child = await _make_child(user.id)
        res = await client.post(f"/v1/matrix/child/{child.id}/interpret", headers=auth_headers,
                                json={"point": FREE_POINT_ID, "lang": "ru"})
        assert res.status_code == 402
        assert "FREE_LIMIT_REACHED" in res.text

    async def test_pro_user_gets_a_stream(self, client, pro_headers, pro_user):
        user, _ = pro_user
        child = await _make_child(user.id)
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream):
            res = await client.post(f"/v1/matrix/child/{child.id}/interpret", headers=pro_headers,
                                    json={"point": "core", "lang": "ru"})
        assert res.status_code == 200
        assert "reading" in res.text

    async def test_unknown_point_is_rejected(self, client, pro_headers, pro_user):
        user, _ = pro_user
        child = await _make_child(user.id)
        res = await client.post(f"/v1/matrix/child/{child.id}/interpret", headers=pro_headers,
                                json={"point": "not_a_point", "lang": "ru"})
        assert res.status_code == 422

    async def test_other_users_child_returns_404(self, client, pro_headers, pro_user):
        other_user, _ = await make_user(email=f"other-{uuid4()}@test.com", tier="pro")
        child = await _make_child(other_user.id)
        res = await client.post(f"/v1/matrix/child/{child.id}/interpret", headers=pro_headers,
                                json={"point": "core", "lang": "ru"})
        assert res.status_code == 404

    async def test_requires_auth(self, client):
        res = await client.post(f"/v1/matrix/child/{uuid4()}/interpret", json={"point": "core"})
        assert res.status_code in (401, 403)


class TestChildMatrixInterpretPrompt:
    async def _capture(self, client, headers, user_id, point="core", lang="ru"):
        child = await _make_child(user_id, label="Alex")
        captured = {}

        def _capturing_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            captured["messages"] = messages
            return _fake_stream(messages, max_tokens, lang, on_finish)

        with patch("app.core.cached_stream.safe_groq_stream", _capturing_stream):
            await client.post(f"/v1/matrix/child/{child.id}/interpret", headers=headers,
                              json={"point": point, "lang": lang})
        return captured["messages"][-1]["content"]

    async def test_prompt_names_the_child(self, client, pro_headers, pro_user):
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id)
        assert "Alex" in prompt

    async def test_prompt_carries_the_whole_matrix(self, client, pro_headers, pro_user):
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id)
        for n in FIXTURE_POINTS:
            assert str(n) in prompt

    async def test_prompt_forbids_fatalistic_labels(self, client, pro_headers, pro_user):
        """Content-safety guard (see childrens_matrix.py's module docstring):
        the AI prompt itself must instruct against flat capability verdicts,
        not just rely on the static data avoiding them."""
        user, _ = pro_user
        prompt = await self._capture(client, pro_headers, user.id)
        assert "не дано" in prompt or "не способен" in prompt


class TestChildArcanaEnergyContentSafety:
    def test_no_fatalistic_or_labeling_framing(self):
        """Same guard as test_money_line.py's, adapted for this module: no
        field here should hand down a flat capability verdict about a
        child. Unlike money_line, there is no separate shadow/block field
        at all — see the module docstring for why."""
        banned_ru = (
            "не дано", "не способен", "никогда не сможет", "обречен", "обречён",
            "не подходит", "невозможно",
        )
        banned_en = (
            "not cut out", "can't do", "cannot do", "never will", "doomed", "impossible",
        )
        for n, entry in CHILD_ARCANA_ENERGY.items():
            for field in ("strength_ru", "support_ru"):
                low = entry[field].lower()
                assert not any(w in low for w in banned_ru), (n, field, entry[field])
            for field in ("strength_en", "support_en"):
                low = entry[field].lower()
                assert not any(w in low for w in banned_en), (n, field, entry[field])

    def test_every_arcana_has_original_ru_en_text(self):
        assert len(CHILD_ARCANA_ENERGY) == 22
        for n, entry in CHILD_ARCANA_ENERGY.items():
            for field in ("strength", "support"):
                assert entry[f"{field}_ru"], n
                assert entry[f"{field}_en"], n

    def test_no_shadow_or_block_field(self):
        """Deliberately only two fields per entry — see module docstring."""
        for entry in CHILD_ARCANA_ENERGY.values():
            assert set(entry.keys()) == {"strength_ru", "support_ru", "strength_en", "support_en"}
