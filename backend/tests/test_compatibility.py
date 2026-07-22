"""POST /compatibility/composite/interpret (TZ-062): req.partner_id (str) was
passed straight into session.get() instead of UUID(req.partner_id), unlike the
other three UUID(...) call sites in this file. Every call crashed with
AttributeError: 'str' object has no attribute 'hex' during SQLAlchemy bind-
parameter processing, before the endpoint's own try/except could turn it into
a clean error. Regression coverage for the fix plus the invalid-format and
other-user edge cases the fix introduces.

"Valid partner_id succeeds" needs the real kerykeion + pyswisseph stack (no
Windows wheel) to actually build a chart, so those run for real only in
Docker/Linux and skip locally, same as tests/test_natal_timezone.py.
"""
from datetime import date, time

from unittest.mock import patch

import pytest
from sqlmodel import select

try:
    import swisseph  # noqa: F401
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False

from app.core.database import AsyncSessionLocal
from app.models.user import UserPartner, UserProfile
from tests.conftest import make_user


async def _make_partner(user_id, birth_date=date(1992, 7, 10), birth_time=None):
    async with AsyncSessionLocal() as session:
        partner = UserPartner(user_id=user_id, label="Partner", birth_date=birth_date, birth_time=birth_time)
        session.add(partner)
        await session.commit()
        await session.refresh(partner)
        return partner


async def _set_profile_birth_time(user_id, hour=14, minute=30):
    async with AsyncSessionLocal() as session:
        result = await session.exec(select(UserProfile).where(UserProfile.user_id == user_id))
        prof = result.first()
        prof.birth_time = time(hour, minute)
        session.add(prof)
        await session.commit()


async def _fake_stream(messages, max_tokens=900, lang="ru"):
    yield 'data: {"text": "ok"}\n\n'
    yield "data: [DONE]\n\n"


class TestCompositeInterpretPartnerId:
    async def test_invalid_partner_id_format_returns_422(self, client, pro_headers):
        res = await client.post(
            "/v1/compatibility/composite/interpret",
            headers=pro_headers,
            json={"partner_id": "not-a-uuid", "lang": "ru", "section": "overview"},
        )
        assert res.status_code == 422

    async def test_other_users_partner_id_returns_404(self, client, pro_user, pro_headers):
        other_user, _ = await make_user(email="other@test.com", tier="pro")
        partner = await _make_partner(other_user.id)

        res = await client.post(
            "/v1/compatibility/composite/interpret",
            headers=pro_headers,
            json={"partner_id": str(partner.id), "lang": "ru", "section": "overview"},
        )
        assert res.status_code == 404


@pytest.mark.skipif(
    not HAS_SWISSEPH,
    reason="pyswisseph has no Windows wheel; real ephemeris only available in Docker/Linux",
)
class TestCompositeInterpretSuccess:
    @pytest.mark.parametrize("section", ["overview", "planets", "aspects", "advice"])
    async def test_valid_partner_id_succeeds(self, client, pro_user, pro_headers, section):
        user, _ = pro_user
        partner = await _make_partner(user.id)

        with patch("app.api.v1.compatibility.safe_groq_stream", _fake_stream):
            res = await client.post(
                "/v1/compatibility/composite/interpret",
                headers=pro_headers,
                json={"partner_id": str(partner.id), "lang": "ru", "section": section},
            )
        assert res.status_code == 200
        assert "ok" in res.text


class TestOverallAggregatesAllSevenTypes:
    """QA-024: /compatibility/overall used to average only signs/elements/
    numerology/chinese, silently ignoring moon/synastry/composite even though
    all three already existed as standalone endpoints. The fix calls those
    three endpoints as-is instead of reimplementing them, so whatever they
    already enforce (birth time for moon, Pro tier for synastry/composite)
    applies here too — a type missing its data/tier is left out of the
    average rather than failing the whole request.
    """

    async def test_default_profile_without_birth_time_keeps_old_four_scores(self, client, auth_headers, auth_user):
        user, _ = auth_user
        partner = await _make_partner(user.id)  # no birth_time on partner, nor on the default profile

        res = await client.post(
            "/v1/compatibility/overall", headers=auth_headers,
            json={"partner_id": str(partner.id), "lang": "ru"},
        )
        assert res.status_code == 200
        assert set(res.json()["scores"].keys()) == {"signs", "elements", "numerology", "chinese"}

    @pytest.mark.skipif(
        not HAS_SWISSEPH,
        reason="pyswisseph has no Windows wheel; real ephemeris only available in Docker/Linux",
    )
    async def test_free_user_gets_moon_but_not_pro_gated_types(self, client, auth_headers, auth_user):
        user, _ = auth_user
        await _set_profile_birth_time(user.id)
        partner = await _make_partner(user.id, birth_time=time(9, 15))

        res = await client.post(
            "/v1/compatibility/overall", headers=auth_headers,
            json={"partner_id": str(partner.id), "lang": "ru"},
        )
        assert res.status_code == 200
        scores = res.json()["scores"]
        assert "moon" in scores
        assert "synastry" not in scores
        assert "composite" not in scores

    @pytest.mark.skipif(
        not HAS_SWISSEPH,
        reason="pyswisseph has no Windows wheel; real ephemeris only available in Docker/Linux",
    )
    async def test_pro_user_with_birth_times_gets_all_seven(self, client, pro_user, pro_headers):
        user, _ = pro_user
        await _set_profile_birth_time(user.id)
        partner = await _make_partner(user.id, birth_time=time(9, 15))

        res = await client.post(
            "/v1/compatibility/overall", headers=pro_headers,
            json={"partner_id": str(partner.id), "lang": "ru"},
        )
        assert res.status_code == 200
        assert set(res.json()["scores"].keys()) == {
            "signs", "elements", "numerology", "chinese", "moon", "synastry", "composite",
        }
