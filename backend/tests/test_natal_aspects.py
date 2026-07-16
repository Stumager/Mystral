"""TZ-076: ASPECT_TYPES had no English names at all — build_full_chart and
natal_transits always returned a Russian aspect name ("Трин", "Квадрат"),
even for lang="en" (and by extension every other language, since English is
the fallback everywhere else in this file). Fixed by giving every aspect a
name_en alongside name_ru, mirroring the PLANET_NAMES_RU/EN pattern already
used a few lines above ASPECT_TYPES.
"""
from unittest.mock import AsyncMock, patch

from app.api.v1.natal import ASPECT_TYPES, _calc_aspects

BODY = {"name": "Test", "year": 1995, "month": 11, "day": 8, "city": "Moscow"}


class TestAspectTypesHaveEnglishNames:
    def test_every_aspect_has_a_distinct_english_name(self):
        for angle, max_orb, atype, name_ru, name_en, symbol in ASPECT_TYPES:
            assert name_en, f"{atype} is missing an English name"
            assert name_en != name_ru

    def test_standard_english_terminology(self):
        names_en = {atype: name_en for _, _, atype, _, name_en, _ in ASPECT_TYPES}
        assert names_en == {
            "conjunction": "Conjunction",
            "sextile": "Sextile",
            "square": "Square",
            "trine": "Trine",
            "opposition": "Opposition",
        }


class TestCalcAspectsIncludesBothLanguages:
    """build_full_chart (used by /natal/calculate) returns both variants
    unconditionally, same as planets/houses in this module — the frontend
    picks the right one at render time."""

    def test_aspect_dict_has_name_ru_and_name_en(self):
        p1 = {"name": "sun", "name_ru": "Солнце", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "abs_pos": 120.0}
        aspects = _calc_aspects([p1, p2])
        assert len(aspects) == 1
        assert aspects[0]["name_ru"] == "Трин"
        assert aspects[0]["name_en"] == "Trine"

    def test_aspect_dict_has_planet_names_in_both_languages(self):
        # TZ-077: NatalChart.tsx's aspect row showed planet1_ru/planet2_ru
        # unconditionally regardless of interface language — the aspect TYPE
        # name (Trine/Трин) was already bilingual since TZ-076, but the
        # planet names next to it weren't. _calc_aspects must expose both.
        p1 = {"name": "sun", "name_ru": "Солнце", "name_en": "Sun", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "name_en": "Moon", "abs_pos": 120.0}
        aspects = _calc_aspects([p1, p2])
        assert aspects[0]["planet1_en"] == "Sun"
        assert aspects[0]["planet2_en"] == "Moon"

    def test_planet_en_falls_back_to_raw_name_if_missing(self):
        p1 = {"name": "sun", "name_ru": "Солнце", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "abs_pos": 120.0}
        aspects = _calc_aspects([p1, p2])
        assert aspects[0]["planet1_en"] == "sun"
        assert aspects[0]["planet2_en"] == "moon"


class TestNatalTransitsAspectLanguage:
    """/natal/transits collapses the aspect to a single "aspect" field
    (unlike build_full_chart's aspects list), so it must pick ru/en itself."""

    def _mock_extract(self, natal_subj, transit_subj):
        def fake_extract(subj, key, ptype="planet"):
            pos = 0.0 if subj is natal_subj else (120.0 if key == "sun" else 50.0)
            return {
                "name": key, "name_ru": key, "name_en": key, "symbol": "?",
                "sign": "Aries", "sign_ru": "Овен", "degree": pos % 30, "abs_pos": pos,
                "house": 1, "retrograde": False, "type": ptype,
            }
        return fake_extract

    async def test_english_lang_returns_english_aspect_name(self, client, auth_headers):
        natal_subj, transit_subj = object(), object()
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", side_effect=[natal_subj, transit_subj]), \
             patch("app.api.v1.natal._extract_planet", side_effect=self._mock_extract(natal_subj, transit_subj)):
            res = await client.post("/v1/natal/transits", headers=auth_headers,
                                     json={**BODY, "lang": "en"})
        assert res.status_code == 200
        transits = res.json()["transits"]
        assert transits, "expected at least one active transit aspect"
        assert transits[0]["aspect"] == "Trine"

    async def test_ru_lang_still_returns_russian_aspect_name(self, client, auth_headers):
        natal_subj, transit_subj = object(), object()
        with patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61))), \
             patch("app.api.v1.natal._build_subject", side_effect=[natal_subj, transit_subj]), \
             patch("app.api.v1.natal._extract_planet", side_effect=self._mock_extract(natal_subj, transit_subj)):
            res = await client.post("/v1/natal/transits", headers=auth_headers,
                                     json={**BODY, "lang": "ru"})
        assert res.status_code == 200
        transits = res.json()["transits"]
        assert transits
        assert transits[0]["aspect"] == "Трин"
