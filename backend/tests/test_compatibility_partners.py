"""TZ-089 QA-001/004/030: creating a partner with an unresolvable birth_city
used to silently accept it (lat/lng just stayed None) while natal/calculate
raised a 422 for the identical input — an inconsistency QA flagged directly.
create_partner now reuses natal.geocode_city, so both endpoints agree. A
partner name had no length cap either, mirroring the natal/calculate gap.
"""
from unittest.mock import patch

from httpx import Response

from tests.test_natal_validation import FakeAsyncClient

BASE = {"name": "Partner", "birth_date": "1995-11-08"}


class TestCreatePartnerCityValidation:
    async def test_unresolvable_city_is_rejected_not_silently_accepted(self, client, auth_headers):
        with patch("app.api.v1.natal.httpx.AsyncClient", FakeAsyncClient([])):
            res = await client.post("/v1/partners", headers=auth_headers,
                                    json={**BASE, "birth_city": "Nonexistentville"})
        assert res.status_code == 422
        assert res.json()["message"] == "Город не найден, проверьте написание"

    async def test_resolvable_city_still_succeeds(self, client, auth_headers):
        payload = [{"lat": "55.75", "lon": "37.61"}]
        with patch("app.api.v1.natal.httpx.AsyncClient", FakeAsyncClient(payload)):
            res = await client.post("/v1/partners", headers=auth_headers,
                                    json={**BASE, "birth_city": "Moscow"})
        assert res.status_code == 200

    async def test_omitted_city_is_still_optional(self, client, auth_headers):
        res = await client.post("/v1/partners", headers=auth_headers, json=BASE)
        assert res.status_code == 200


class TestCreatePartnerNameValidation:
    async def test_oversized_name_rejected(self, client, auth_headers):
        res = await client.post("/v1/partners", headers=auth_headers,
                                json={**BASE, "name": "A" * 5000})
        assert res.status_code == 422

    async def test_empty_name_rejected(self, client, auth_headers):
        res = await client.post("/v1/partners", headers=auth_headers,
                                json={**BASE, "name": ""})
        assert res.status_code == 422
