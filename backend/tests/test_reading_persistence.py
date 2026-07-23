"""Daily/yearly readings must persist across section re-entry instead of
re-rolling. Three features shared one root cause: the draw endpoints
(/tarot/spread, /runes/draw) always generated fresh randomness and never read
back an already-drawn reading for the current period — the reading tables were
written on every draw but only ever read by the /history endpoints. Fixed by a
period-aware read-back (day for card/rune of the day, year for the year spread)
that returns the existing reading unless force=true (the explicit "New spread"
button).
"""
import json
from datetime import datetime, timedelta

from sqlmodel import select

from app.core.database import AsyncSessionLocal
from app.data.runes import RUNE_BY_ID
from app.api.v1.runes import _rune_out
from app.models.user import RuneReading, TarotReading


def _tarot(client, headers, **extra):
    return client.post("/v1/tarot/spread", headers=headers,
                       json={"spread_id": "card_of_day", "lang": "ru", **extra})


def _rune(client, headers, spread="rune_of_day", **extra):
    return client.post("/v1/runes/draw", headers=headers,
                       json={"spread_type": spread, "lang": "ru", **extra})


class TestTarotCardOfDayPersistence:
    async def test_reentry_returns_same_card(self, client, pro_headers):
        first = await _tarot(client, pro_headers)
        assert first.status_code == 200
        d1 = first.json()
        assert d1["persisted"] is False

        second = await _tarot(client, pro_headers)
        d2 = second.json()
        assert d2["persisted"] is True
        assert d2["reading_id"] == d1["reading_id"]
        assert [c["id"] for c in d2["cards"]] == [c["id"] for c in d1["cards"]]
        assert d2["cards"][0]["reversed"] == d1["cards"][0]["reversed"]

    async def test_force_draws_new(self, client, pro_headers):
        d1 = (await _tarot(client, pro_headers)).json()
        forced = (await _tarot(client, pro_headers, force=True)).json()
        assert forced["persisted"] is False
        assert forced["reading_id"] != d1["reading_id"]

    async def test_reentries_do_not_create_extra_rows(self, client, pro_headers):
        for _ in range(3):
            await _tarot(client, pro_headers)
        async with AsyncSessionLocal() as s:
            rows = (await s.exec(
                select(TarotReading).where(TarotReading.spread_id == "card_of_day")
            )).all()
        assert len(rows) == 1

    async def test_yesterdays_reading_triggers_new_draw(self, client, pro_headers, pro_user):
        user, _ = pro_user
        async with AsyncSessionLocal() as s:
            s.add(TarotReading(
                user_id=user.id, spread_id="card_of_day",
                cards_json=json.dumps([{"id": 0, "reversed": False}]),
                created_at=datetime.utcnow() - timedelta(days=1),
            ))
            await s.commit()
        res = await _tarot(client, pro_headers)
        assert res.json()["persisted"] is False

    async def test_non_period_spread_always_fresh(self, client, pro_headers):
        r1 = await client.post("/v1/tarot/spread", headers=pro_headers,
                               json={"spread_id": "three_cards", "lang": "ru"})
        r2 = await client.post("/v1/tarot/spread", headers=pro_headers,
                               json={"spread_id": "three_cards", "lang": "ru"})
        assert r1.json()["persisted"] is False
        assert r2.json()["persisted"] is False
        assert r1.json()["reading_id"] != r2.json()["reading_id"]

    async def test_free_reentry_returns_card_not_paywall(self, client, auth_headers):
        """Regression: a free user re-entering the section must see their
        card, not the 402/paywall the daily rate-limit used to raise."""
        first = await _tarot(client, auth_headers)
        assert first.status_code == 200
        second = await _tarot(client, auth_headers)
        assert second.status_code == 200
        assert second.json()["persisted"] is True


class TestRuneOfDayPersistence:
    async def test_reentry_returns_same_rune(self, client, pro_headers):
        d1 = (await _rune(client, pro_headers)).json()
        assert d1["persisted"] is False

        d2 = (await _rune(client, pro_headers)).json()
        assert d2["persisted"] is True
        assert [r["id"] for r in d2["drawn_runes"]] == [r["id"] for r in d1["drawn_runes"]]
        assert d2["drawn_runes"][0]["reversed"] == d1["drawn_runes"][0]["reversed"]

    async def test_force_draws_new(self, client, pro_headers):
        await _rune(client, pro_headers)
        forced = (await _rune(client, pro_headers, force=True)).json()
        assert forced["persisted"] is False

    async def test_reconstruction_follows_request_language(self, client, pro_headers):
        """Drawn in ru, re-viewed in en: only id/reversed are period-stable,
        so names must be re-derived in the current language."""
        drew = (await _rune(client, pro_headers)).json()
        rid = drew["drawn_runes"][0]["id"]
        rev = drew["drawn_runes"][0]["reversed"]
        en = await client.post("/v1/runes/draw", headers=pro_headers,
                               json={"spread_type": "rune_of_day", "lang": "en"})
        d = en.json()
        assert d["persisted"] is True
        assert d["drawn_runes"][0]["name"] == _rune_out(RUNE_BY_ID[rid], "en", rev)["name"]

    async def test_free_reentry_returns_rune_not_paywall(self, client, auth_headers):
        first = await _rune(client, auth_headers)
        assert first.status_code == 200
        second = await _rune(client, auth_headers)
        assert second.status_code == 200
        assert second.json()["persisted"] is True


class TestYearSpreadPersistence:
    async def test_reentry_returns_same_thirteen(self, client, pro_headers):
        d1 = (await _rune(client, pro_headers, spread="year_spread")).json()
        assert d1["persisted"] is False
        assert len(d1["drawn_runes"]) == 13

        d2 = (await _rune(client, pro_headers, spread="year_spread")).json()
        assert d2["persisted"] is True
        assert [r["id"] for r in d2["drawn_runes"]] == [r["id"] for r in d1["drawn_runes"]]

    async def test_force_draws_new(self, client, pro_headers):
        await _rune(client, pro_headers, spread="year_spread")
        forced = (await _rune(client, pro_headers, spread="year_spread", force=True)).json()
        assert forced["persisted"] is False

    async def test_last_years_reading_triggers_new_draw(self, client, pro_headers, pro_user):
        user, _ = pro_user
        async with AsyncSessionLocal() as s:
            s.add(RuneReading(
                user_id=user.id, spread_type="year_spread",
                runes_json=json.dumps([{"id": "fehu", "reversed": False, "position": "x"}]),
                created_at=datetime(datetime.utcnow().year - 1, 6, 1),
            ))
            await s.commit()
        res = await _rune(client, pro_headers, spread="year_spread")
        assert res.json()["persisted"] is False

    async def test_non_period_rune_spread_always_fresh(self, client, pro_headers):
        r1 = await _rune(client, pro_headers, spread="runic_cross")
        r2 = await _rune(client, pro_headers, spread="runic_cross")
        assert r1.json()["persisted"] is False
        assert r2.json()["persisted"] is False
