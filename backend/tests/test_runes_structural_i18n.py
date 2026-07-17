"""TZ-080: runes.py's meanings, spread names/positions, and stave content
were all ru/en-only. Fixed via the shared structural_i18n helpers (pick/
pick_list), backed by runes_i18n.py, with English as the fallback until a
language is actually generated. This is a BATCHED section — see
test_generate_structural_translations.py for the batching mechanics; this
file covers the read-side wiring only.
"""
from unittest.mock import patch

from app.api.v1.runes import _rune_out, _spread_desc, _spread_name, _spread_positions
from app.data import runes_i18n
from app.data.runes import RUNE_BY_ID, SPREADS_RUNES
from app.data.staves import STAVES


class TestRuneOutI18n:
    def test_ru_and_en_unaffected(self):
        fehu = RUNE_BY_ID["fehu"]
        assert _rune_out(fehu, "ru")["name"] == "Феху"
        assert _rune_out(fehu, "en")["name"] == "Fehu"

    def test_es_falls_back_to_english_until_generated(self):
        fehu = RUNE_BY_ID["fehu"]
        with patch.dict(runes_i18n.RUNES_I18N, {"es": {}}):
            out = _rune_out(fehu, "es")
        assert out["name"] == "Fehu"
        assert out["deity"] == "Freya"
        assert out["meaning"] == fehu["meaning_en"]

    def test_es_uses_i18n_once_populated(self):
        fehu = RUNE_BY_ID["fehu"]
        with patch.dict(runes_i18n.RUNES_I18N, {"es": {"fehu": {"name": "Fehu-ES", "meaning": "ES meaning"}}}):
            out = _rune_out(fehu, "es")
            assert out["name"] == "Fehu-ES"
            assert out["meaning"] == "ES meaning"
            # Field not yet generated still falls back to English.
            assert out["deity"] == "Freya"

    def test_reversed_meaning_selected_when_reversed_and_reversible(self):
        fehu = RUNE_BY_ID["fehu"]  # can_reverse: True
        out = _rune_out(fehu, "en", reversed=True)
        assert out["meaning"] == fehu["reversed_meaning_en"]

    def test_non_reversible_rune_ignores_reversed_flag(self):
        gebo = RUNE_BY_ID["gebo"]  # can_reverse: False
        out = _rune_out(gebo, "en", reversed=True)
        assert out["meaning"] == gebo["meaning_en"]


class TestSpreadI18n:
    def test_ru_and_en_unaffected(self):
        spread = SPREADS_RUNES["rune_of_day"]
        assert _spread_name("rune_of_day", spread, "ru") == "Руна дня"
        assert _spread_name("rune_of_day", spread, "en") == "Rune of the Day"

    def test_es_falls_back_to_english(self):
        spread = SPREADS_RUNES["rune_of_day"]
        with patch.dict(runes_i18n.SPREADS_RUNES_I18N, {"es": {}}):
            assert _spread_name("rune_of_day", spread, "es") == "Rune of the Day"
            assert _spread_desc("rune_of_day", spread, "es") == spread["desc_en"]
            assert _spread_positions("rune_of_day", spread, "es") == spread["positions_en"]

    def test_es_uses_i18n_once_populated(self):
        spread = SPREADS_RUNES["three_norns"]
        with patch.dict(runes_i18n.SPREADS_RUNES_I18N, {"es": {"three_norns": {
            "name": "Tres Nornas", "positions_0": "Urd (Pasado)",
        }}}):
            assert _spread_name("three_norns", spread, "es") == "Tres Nornas"
            positions = _spread_positions("three_norns", spread, "es")
            assert positions[0] == "Urd (Pasado)"
            # positions 1/2 not yet generated - fall back to English individually
            assert positions[1] == spread["positions_en"][1]


class TestStavesEndpointI18n:
    async def test_defaults_to_russian(self, client):
        res = await client.get("/v1/runes/staves")
        assert res.status_code == 200
        protection = next(s for s in res.json() if s["id"] == "protection")
        assert protection["name"] == "Став Защиты"

    async def test_en_lang(self, client):
        res = await client.get("/v1/runes/staves?lang=en")
        assert res.status_code == 200
        protection = next(s for s in res.json() if s["id"] == "protection")
        assert protection["name"] == "Protection Stave"

    async def test_es_falls_back_to_english_until_generated(self, client):
        with patch.dict(runes_i18n.STAVES_I18N, {"es": {}}):
            res = await client.get("/v1/runes/staves?lang=es")
        assert res.status_code == 200
        protection = next(s for s in res.json() if s["id"] == "protection")
        assert protection["name"] == "Protection Stave"


class TestSpreadsEndpointI18n:
    async def test_es_falls_back_to_english_until_generated(self, client):
        with patch.dict(runes_i18n.SPREADS_RUNES_I18N, {"es": {}}):
            res = await client.get("/v1/runes/spreads?lang=es")
        assert res.status_code == 200
        rune_of_day = next(s for s in res.json() if s["id"] == "rune_of_day")
        assert rune_of_day["name"] == "Rune of the Day"
        assert rune_of_day["positions"] == ["Day's message"]
