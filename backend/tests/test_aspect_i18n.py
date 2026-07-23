# -*- coding: utf-8 -*-
"""Group A (QA-011): natal.py ASPECT_TYPES carried only ru+en, so es/pt/tr/uk
showed English aspect names ("Conjunction", "Trine") in the natal chart,
transits and compatibility synastry — right next to correctly-localized
planet names. _aspect_name now resolves all six languages; the chart exposes
it as each aspect's `name_local`, matching how planet/sign names already work.
"""
from app.api.v1.natal import _aspect_name


class TestAspectNameResolver:
    def test_ru_and_en_from_inline_values(self):
        assert _aspect_name("trine", "Трин", "Trine", "ru") == "Трин"
        assert _aspect_name("trine", "Трин", "Trine", "en") == "Trine"

    def test_all_four_extra_languages(self):
        assert _aspect_name("conjunction", "Соединение", "Conjunction", "es") == "Conjunción"
        assert _aspect_name("conjunction", "Соединение", "Conjunction", "pt") == "Conjunção"
        assert _aspect_name("opposition", "Оппозиция", "Opposition", "tr") == "Karşıtlık"
        assert _aspect_name("trine", "Трин", "Trine", "uk") == "Тригон"

    def test_unknown_language_falls_back_to_english(self):
        assert _aspect_name("sextile", "Секстиль", "Sextile", "de") == "Sextile"

    def test_every_aspect_has_all_languages(self):
        from app.api.v1.natal import ASPECT_TYPES, ASPECT_NAMES_I18N
        atypes = {a[2] for a in ASPECT_TYPES}
        for lang, table in ASPECT_NAMES_I18N.items():
            assert set(table) == atypes, f"{lang} missing/extra aspect keys"


class TestChartExposesLocalAspectName:
    async def test_natal_calculate_returns_localized_aspect(self, client, pro_headers):
        from unittest.mock import patch, MagicMock

        fake_chart = {
            "planets": [], "extra_points": [], "houses": [], "ascendant": {},
            "midheaven": {}, "part_of_fortune": None, "stelliums": [],
            "element_balance": {}, "modality_balance": {},
            "dominant_sign": "", "dominant_sign_ru": "", "dominant_sign_local": "",
            "aspects": [{
                "planet1": "sun", "planet2": "moon", "type": "trine",
                "name_ru": "Трин", "name_en": "Trine", "name_local": "Trígono",
                "symbol": "△", "orb": 1.2, "harmony": True,
            }],
        }
        body = {"name": "Test", "year": 1995, "month": 11, "day": 8, "city": "Madrid", "lang": "es"}
        with patch("app.api.v1.natal.geocode_city", new=_amock((40.4, -3.7))), \
             patch("app.api.v1.natal._build_subject", return_value=MagicMock()), \
             patch("app.api.v1.natal.build_full_chart", return_value=fake_chart):
            res = await client.post("/v1/natal/calculate", headers=pro_headers, json=body)
        assert res.status_code == 200
        assert res.json()["aspects"][0]["name_local"] == "Trígono"


def _amock(value):
    async def _f(*a, **k):
        return value
    return _f
