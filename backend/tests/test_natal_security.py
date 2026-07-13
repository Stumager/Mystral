"""TZ-067: /natal/calculate and /natal/svg had no auth and no rate limit —
any unauthenticated request could trigger a full geocode + kerykeion/
pyswisseph calculation (and, for /svg, temp-file SVG generation). Worse than
the already-closed horoscope/stream gap per the audit. Fixed by adding
Depends(get_current_user) + check_rate_limit(...), the same pattern already
used by natal_interpret/lunar_ai/etc — not a new mechanism.

Real kerykeion/pyswisseph calculation isn't needed to test the auth/rate-limit
wrapper itself, so geocode_city/_build_subject/build_full_chart are mocked —
this also means these tests run on Windows (no pyswisseph wheel), unlike
test_natal_timezone.py.
"""
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

BODY = {"name": "Test", "year": 1995, "month": 11, "day": 8, "city": "Moscow"}


class TestNatalCalculateSecurity:
    async def test_requires_auth(self, client):
        res = await client.post("/v1/natal/calculate", json=BODY)
        assert res.status_code == 401

    async def test_works_with_token_within_limit(self, client, auth_headers):
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json=BODY)
        assert res.status_code == 200

    async def test_rate_limited_after_threshold(self, client, auth_headers):
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            for _ in range(10):
                res = await client.post("/v1/natal/calculate", headers=auth_headers, json=BODY)
                assert res.status_code == 200
            over_limit = await client.post("/v1/natal/calculate", headers=auth_headers, json=BODY)
        assert over_limit.status_code == 429

    async def test_rate_limit_is_per_user(self, client, auth_headers, pro_headers):
        """One user hitting the limit must not affect another user's quota."""
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            for _ in range(10):
                res = await client.post("/v1/natal/calculate", headers=auth_headers, json=BODY)
                assert res.status_code == 200
            blocked = await client.post("/v1/natal/calculate", headers=auth_headers, json=BODY)
            assert blocked.status_code == 429

            other_user_res = await client.post("/v1/natal/calculate", headers=pro_headers, json=BODY)
        assert other_user_res.status_code == 200


class TestNatalSvgSecurity:
    async def test_requires_auth(self, client):
        res = await client.post("/v1/natal/svg", json=BODY)
        assert res.status_code == 401

    async def test_works_with_token_within_limit(self, client, auth_headers):
        fake_tmp = MagicMock()
        fake_tmp.name = "fake_tmp.svg"
        fake_tmp_cm = MagicMock()
        fake_tmp_cm.__enter__ = MagicMock(return_value=fake_tmp)
        fake_tmp_cm.__exit__ = MagicMock(return_value=False)

        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("tempfile.NamedTemporaryFile", return_value=fake_tmp_cm), \
             patch("kerykeion.KerykeionChartSVG", return_value=MagicMock(makeSVG=MagicMock())), \
             patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="<svg>fake</svg>")), \
             patch("os.unlink"):
            res = await client.post("/v1/natal/svg", headers=auth_headers, json=BODY)
        assert res.status_code == 200

    async def test_rate_limited_after_threshold(self, client, auth_headers):
        """The over-limit request never reaches geocode/kerykeion at all —
        check_rate_limit is the first line of the handler — so warm-up calls
        don't need the full SVG-generation mock chain to prove the 11th
        request is rejected."""
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))):
            for _ in range(10):
                await client.post("/v1/natal/svg", headers=auth_headers, json=BODY)
            over_limit = await client.post("/v1/natal/svg", headers=auth_headers, json=BODY)
        assert over_limit.status_code == 429
