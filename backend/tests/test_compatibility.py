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
from datetime import date
from unittest.mock import patch

import pytest

try:
    import swisseph  # noqa: F401
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False

from app.core.database import AsyncSessionLocal
from app.models.user import UserPartner
from tests.conftest import make_user


async def _make_partner(user_id, birth_date=date(1992, 7, 10)):
    async with AsyncSessionLocal() as session:
        partner = UserPartner(user_id=user_id, label="Partner", birth_date=birth_date)
        session.add(partner)
        await session.commit()
        await session.refresh(partner)
        return partner


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
