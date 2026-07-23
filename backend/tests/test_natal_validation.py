"""TZ-089:
QA-029 — a direct POST with month=13/day=32 reached kerykeion and came back
  as a raw HTTP 500. NatalRequest now bounds day/month/hour/minute and
  validates the resulting calendar date, so invalid input never leaves the
  request-parsing layer (a clean 422 instead).
QA-030 — `name` had no length cap (5000 chars was accepted, HTTP 200).
  Capped at 100 chars, same as the frontend's own (much tighter) 50-char rule.
QA-001/004 — natal raised a raw, English-only "City not found: {city}" 422;
  compatibility's partner endpoint silently accepted the same bad city
  (lat/lng just stayed None). Both now go through natal.geocode_city and its
  shared, localized message.
QA-002 — omitting birth time used to silently default to noon with no signal
  anywhere in the response. hour/minute are now Optional; omitting them still
  works, but the response says so via time_known/time_used.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from httpx import Response

from app.api.v1.natal import geocode_city

BASE = {"name": "Test", "year": 1995, "month": 11, "day": 8, "city": "Moscow"}


class FakeAsyncClient:
    """Stands in for httpx.AsyncClient in geocode_city, returning a
    configurable Nominatim-shaped payload."""

    def __init__(self, payload):
        self.payload = payload

    def __call__(self, *a, **k):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def get(self, *a, **k):
        return Response(200, json=self.payload)


class TestGeocodeCityNotFound:
    async def test_raises_localized_422_ru(self):
        with patch("app.api.v1.natal.httpx.AsyncClient", FakeAsyncClient([])):
            with pytest.raises(HTTPException) as exc:
                await geocode_city("Nonexistentville", "ru")
        assert exc.value.status_code == 422
        assert exc.value.detail == "Город не найден, проверьте написание"

    async def test_raises_localized_422_en(self):
        with patch("app.api.v1.natal.httpx.AsyncClient", FakeAsyncClient([])):
            with pytest.raises(HTTPException) as exc:
                await geocode_city("Nonexistentville", "en")
        assert exc.value.status_code == 422
        assert exc.value.detail == "City not found, check the spelling"

    async def test_found_city_returns_coords(self):
        payload = [{"lat": "55.75", "lon": "37.61"}]
        with patch("app.api.v1.natal.httpx.AsyncClient", FakeAsyncClient(payload)):
            lat, lon = await geocode_city("Moscow", "ru")
        assert (lat, lon) == (55.75, 37.61)


class TestNatalCalculateFieldValidation:
    async def test_invalid_month_rejected_before_calculation(self, client, auth_headers):
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "month": 13})
        assert res.status_code == 422

    async def test_invalid_day_rejected_before_calculation(self, client, auth_headers):
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "day": 32})
        assert res.status_code == 422

    async def test_nonexistent_calendar_date_rejected(self, client, auth_headers):
        """Feb 30 passes the plain 1-31 day bound but isn't a real date."""
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "month": 2, "day": 30})
        assert res.status_code == 422

    async def test_out_of_range_hour_rejected(self, client, auth_headers):
        res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "hour": 24})
        assert res.status_code == 422

    async def test_out_of_range_minute_rejected(self, client, auth_headers):
        res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "minute": 60})
        assert res.status_code == 422

    async def test_oversized_name_rejected(self, client, auth_headers):
        res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "name": "A" * 5000})
        assert res.status_code == 422

    async def test_empty_name_rejected(self, client, auth_headers):
        res = await client.post("/v1/natal/calculate", headers=auth_headers, json={**BASE, "name": ""})
        assert res.status_code == 422

    async def test_valid_request_still_works(self, client, auth_headers):
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json=BASE)
        assert res.status_code == 200


class TestNatalCalculateApproximateTime:
    async def test_time_omitted_flags_result_as_approximate(self, client, auth_headers):
        body = {k: v for k, v in BASE.items()}  # no hour/minute at all
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json=body)
        assert res.status_code == 200
        data = res.json()
        assert data["time_known"] is False
        assert data["time_used"] == "12:00"

    async def test_time_provided_is_not_flagged_approximate(self, client, auth_headers):
        body = {**BASE, "hour": 14, "minute": 30}
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json=body)
        assert res.status_code == 200
        data = res.json()
        assert data["time_known"] is True
        assert data["time_used"] == "14:30"

    async def test_explicit_midnight_is_not_treated_as_unknown(self, client, auth_headers):
        """hour=0 is a real, explicit answer — must not be confused with
        'not provided' (which is None, not 0)."""
        body = {**BASE, "hour": 0, "minute": 0}
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value={"planets": []}):
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json=body)
        assert res.status_code == 200
        assert res.json()["time_known"] is True
