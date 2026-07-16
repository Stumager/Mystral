"""TZ-080: compatibility.py's sign/element/chinese-zodiac labels and the
synastry endpoint's planet/aspect names were `ru else en` ternaries — an
ES/PT/TR/UK interface always silently got English. Fixed via the shared
structural_i18n helper (app.core.structural_i18n) plus companion
compatibility_i18n.py modules, with English as the fallback until those
modules are actually populated by the translate script.
"""
from unittest.mock import AsyncMock, patch

from app.api.v1.compatibility import (
    CHINESE, CHINESE_RU, ELEMENTS_EN, ELEMENTS_RU, SIGNS, SIGNS_RU,
    _chinese_name, _element_name, _sign_name,
)
from app.core.structural_i18n import localized_field, pick


class TestStructuralI18nHelpers:
    def test_localized_field_falls_back_to_en_when_missing(self):
        assert localized_field({"es": {}}, "es", "aries", "name", "Aries") == "Aries"

    def test_localized_field_uses_generated_value_when_present(self):
        i18n = {"es": {"aries": {"name": "Carnero"}}}
        assert localized_field(i18n, "es", "aries", "name", "Aries") == "Carnero"

    def test_pick_uses_ru_directly(self):
        base = {"name_ru": "Феху", "name_en": "Fehu"}
        assert pick(base, "name", "ru") == "Феху"

    def test_pick_falls_back_to_en_without_i18n_module(self):
        base = {"name_ru": "Феху", "name_en": "Fehu"}
        assert pick(base, "name", "es") == "Fehu"

    def test_pick_uses_i18n_module_when_present(self):
        base = {"name_ru": "Феху", "name_en": "Fehu"}
        i18n = {"es": {"fehu": {"name": "Fehu-ES"}}}
        assert pick(base, "name", "es", i18n_module=i18n, key="fehu") == "Fehu-ES"


class TestCompatibilityLabelHelpers:
    def test_sign_name_ru(self):
        assert _sign_name(0, "ru") == SIGNS_RU[0]

    def test_sign_name_en(self):
        assert _sign_name(0, "en") == SIGNS[0]

    def test_sign_name_es_falls_back_to_english_until_generated(self):
        assert _sign_name(0, "es") == SIGNS[0]

    def test_sign_name_es_uses_i18n_once_populated(self):
        from app.data import compatibility_i18n
        with patch.dict(compatibility_i18n.SIGNS_I18N, {"es": {"0": {"name": "Aries-ES"}}}):
            assert _sign_name(0, "es") == "Aries-ES"

    def test_element_name_fallback(self):
        assert _element_name(0, "tr") == ELEMENTS_EN[0]
        assert _element_name(0, "ru") == ELEMENTS_RU[0]

    def test_chinese_name_fallback(self):
        assert _chinese_name(0, "uk") == CHINESE[0]
        assert _chinese_name(0, "ru") == CHINESE_RU[0]


class TestCompatEndpointsUseHelpers:
    async def _make_partner(self, client, auth_headers):
        res = await client.post("/v1/partners", headers=auth_headers,
                                 json={"name": "Partner", "birth_date": "1998-04-10"})
        assert res.status_code == 200
        return res.json()["id"]

    async def test_signs_endpoint_es_lang_does_not_crash_and_falls_back_to_en(self, client, auth_headers):
        pid = await self._make_partner(client, auth_headers)
        res = await client.post("/v1/compatibility/signs", headers=auth_headers,
                                 json={"partner_id": pid, "lang": "es"})
        assert res.status_code == 200
        data = res.json()
        assert data["user_sign"] in SIGNS  # falls back to English name, not Russian, not a crash
        assert data["description"]  # _DESCS already covers es

    async def test_signs_endpoint_ru_lang_unaffected(self, client, auth_headers):
        pid = await self._make_partner(client, auth_headers)
        res = await client.post("/v1/compatibility/signs", headers=auth_headers,
                                 json={"partner_id": pid, "lang": "ru"})
        assert res.status_code == 200
        assert res.json()["user_sign"] in SIGNS_RU


class TestSynastryLanguageSelection:
    """/compatibility/synastry used to build planet names from a
    Russian-only local dict and always return the Russian aspect name,
    regardless of req.lang. Reproduce via mocked kerykeion subjects, same
    approach as test_natal_aspects.py."""

    def _mock_subject(self, sun_pos, moon_pos):
        class Planet:
            def __init__(self, abs_pos):
                self.abs_pos = abs_pos
                self.position = abs_pos
        subj = type("S", (), {})()
        subj.sun = Planet(sun_pos)
        subj.moon = Planet(moon_pos)
        for k in ("mercury", "venus", "mars", "jupiter", "saturn"):
            setattr(subj, k, None)
        return subj

    async def test_english_lang_returns_english_planet_and_aspect_names(self, client, pro_headers):
        res = await client.post("/v1/partners", headers=pro_headers,
                                 json={"name": "Partner", "birth_date": "1998-04-10"})
        pid = res.json()["id"]

        user_subj = self._mock_subject(0.0, 0.0)
        partner_subj = self._mock_subject(120.0, 0.0)
        with patch("kerykeion.AstrologicalSubject", side_effect=[user_subj, partner_subj]):
            out = await client.post("/v1/compatibility/synastry", headers=pro_headers,
                                     json={"partner_id": pid, "lang": "en"})
        assert out.status_code == 200
        aspects = out.json()["aspects"]
        assert aspects
        assert aspects[0]["user_planet"] == "Sun"
        assert aspects[0]["partner_planet"] == "Sun"
        assert aspects[0]["aspect"] == "Trine"

    async def test_ru_lang_still_returns_russian_names(self, client, pro_headers):
        res = await client.post("/v1/partners", headers=pro_headers,
                                 json={"name": "Partner", "birth_date": "1998-04-10"})
        pid = res.json()["id"]

        user_subj = self._mock_subject(0.0, 0.0)
        partner_subj = self._mock_subject(120.0, 0.0)
        with patch("kerykeion.AstrologicalSubject", side_effect=[user_subj, partner_subj]):
            out = await client.post("/v1/compatibility/synastry", headers=pro_headers,
                                     json={"partner_id": pid, "lang": "ru"})
        assert out.status_code == 200
        aspects = out.json()["aspects"]
        assert aspects
        assert aspects[0]["user_planet"] == "Солнце"
        assert aspects[0]["aspect"] == "Трин"
