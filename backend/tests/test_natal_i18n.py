"""TZ-080: natal.py's planet and zodiac sign names were ru/en-only
everywhere (build_full_chart, natal_transits) — an ES/PT/TR/UK interface
always got the English name. Fixed via _planet_name()/_sign_name(), backed
by natal_i18n.py, with English as the fallback until a language is
generated. Aspect names (already ru/en from TZ-076/079) and the 5 long
interpretation prompt templates are out of scope here (separate work).
"""
from unittest.mock import patch

from app.api.v1.natal import (
    PLANET_NAMES_EN, PLANET_NAMES_RU, SIGN_ORDER, _planet_name, _sign_name,
)
from app.data import natal_i18n


class TestPlanetNameHelper:
    def test_ru_returns_russian_name(self):
        assert _planet_name("sun", "ru") == PLANET_NAMES_RU["sun"]

    def test_en_returns_english_name(self):
        assert _planet_name("sun", "en") == PLANET_NAMES_EN["sun"]

    def test_es_falls_back_to_english_until_generated(self):
        with patch.dict(natal_i18n.PLANET_NAMES_I18N, {"es": {}}):
            assert _planet_name("sun", "es") == PLANET_NAMES_EN["sun"]

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(natal_i18n.PLANET_NAMES_I18N, {"es": {"sun": {"name": "Sol"}}}):
            assert _planet_name("sun", "es") == "Sol"


class TestSignNameHelper:
    def test_ru_returns_russian_sign(self):
        assert _sign_name("Aries", "ru") == "Овен"

    def test_en_returns_normalized_english_sign(self):
        assert _sign_name("Ari", "en") == "Aries"

    def test_es_falls_back_to_english_until_generated(self):
        assert _sign_name("Aries", "es") == "Aries"

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(natal_i18n.SIGNS_I18N, {"es": {"Aries": {"name": "Aries-ES"}}}):
            assert _sign_name("Aries", "es") == "Aries-ES"

    def test_every_sign_in_sign_order_resolves(self):
        for sign in SIGN_ORDER:
            assert _sign_name(sign, "ru")
            assert _sign_name(sign, "en") == sign


class TestBuildFullChartThreadsLang:
    """build_full_chart/_extract_planet gained name_local/sign_local fields
    additively — existing name/name_ru/name_en/sign/sign_ru fields are
    untouched, so this only checks the new fields resolve correctly."""

    def test_extract_planet_default_lang_is_ru(self):
        from app.api.v1.natal import _extract_planet

        class FakeSign:
            sign = "Ari"
            position = 10.0
            abs_pos = 10.0
            house = "First_House"
            retrograde = False

        class FakeSubj:
            sun = FakeSign()

        result = _extract_planet(FakeSubj(), "sun")
        assert result["name_local"] == PLANET_NAMES_RU["sun"]
        assert result["sign_local"] == "Овен"

    def test_extract_planet_with_explicit_lang(self):
        from app.api.v1.natal import _extract_planet

        class FakeSign:
            sign = "Ari"
            position = 10.0
            abs_pos = 10.0
            house = "First_House"
            retrograde = False

        class FakeSubj:
            sun = FakeSign()

        result = _extract_planet(FakeSubj(), "sun", lang="en")
        assert result["name_local"] == PLANET_NAMES_EN["sun"]
        assert result["sign_local"] == "Aries"
