"""TZ-080: lunar.py's day/sign/event/phase content was all ru/en-only —
an ES/PT/TR/UK interface always got English regardless of VALID_LANGS
already accepting all 6. Fixed via the shared structural_i18n helpers,
backed by lunar_i18n.py, with English as the fallback until a language is
actually generated. Moon sign *names* reuse natal_i18n.SIGNS_I18N rather
than being translated a second time. This is a BATCHED section — see
test_generate_structural_translations.py for the batching mechanics.
"""
from unittest.mock import patch

from app.api.v1.lunar import (
    EVENT_DATA,
    PHASE_NAMES_EN,
    PHASE_NAMES_RU,
    SIGNS,
    SIGNS_RU,
    _event_field,
    _phase_name,
    _sign_name,
    get_lunar_today_data,
)
from app.data import lunar_i18n, natal_i18n
from app.data.lunar_days import LUNAR_DAYS
from app.data.moon_signs import MOON_SIGNS


class TestSignNameReusesNatalI18n:
    def test_ru_and_en(self):
        assert _sign_name(0, "ru") == SIGNS_RU[0]
        assert _sign_name(0, "en") == SIGNS[0]

    def test_es_falls_back_to_english_until_generated(self):
        assert _sign_name(0, "es") == SIGNS[0]

    def test_es_uses_natal_i18n_directly_no_separate_lunar_copy(self):
        # Populating natal_i18n.SIGNS_I18N (not a lunar-specific dict) must
        # be enough - proves the reuse, not a duplicate translation.
        with patch.dict(natal_i18n.SIGNS_I18N, {"es": {"Aries": {"name": "Aries-ES"}}}):
            assert _sign_name(0, "es") == "Aries-ES"


class TestPhaseNames:
    def test_ru_and_en(self):
        assert _phase_name(0, "ru") == PHASE_NAMES_RU[0]
        assert _phase_name(0, "en") == PHASE_NAMES_EN[0]

    def test_es_falls_back_to_english(self):
        assert _phase_name(0, "es") == PHASE_NAMES_EN[0]

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(lunar_i18n.PHASE_NAMES_I18N, {"es": {"0": {"name": "Luna Nueva"}}}):
            assert _phase_name(0, "es") == "Luna Nueva"


class TestEventField:
    def test_ru_and_en(self):
        ed = EVENT_DATA["new_moon"]
        assert _event_field(ed, "title", "new_moon", "ru") == ed["title_ru"]
        assert _event_field(ed, "title", "new_moon", "en") == ed["title_en"]

    def test_es_falls_back_to_english(self):
        ed = EVENT_DATA["new_moon"]
        assert _event_field(ed, "title", "new_moon", "es") == ed["title_en"]

    def test_es_uses_i18n_once_populated(self):
        ed = EVENT_DATA["new_moon"]
        with patch.dict(lunar_i18n.EVENT_DATA_I18N, {"es": {"new_moon": {"title": "Luna Nueva ES"}}}):
            assert _event_field(ed, "title", "new_moon", "es") == "Luna Nueva ES"


class TestGetLunarTodayData:
    def test_es_falls_back_to_english_for_day_and_sign_content(self):
        data = get_lunar_today_data("es")
        ld = data["lunar_day"]
        day_en = LUNAR_DAYS[ld]
        assert data["day_title"] == day_en["title_en"]
        assert data["favorable"] == day_en["favorable_en"]
        sign_en = MOON_SIGNS[data["moon_sign_key"]]
        assert data["sign_desc"] == sign_en["desc_en"]
        assert data["sign_favorable"] == sign_en["favorable_en"]

    def test_ru_unaffected(self):
        data = get_lunar_today_data("ru")
        ld = data["lunar_day"]
        assert data["day_title"] == LUNAR_DAYS[ld]["title_ru"]

    def test_es_uses_i18n_once_populated(self):
        data_before = get_lunar_today_data("es")
        ld = data_before["lunar_day"]
        sign_key = data_before["moon_sign_key"]
        with patch.dict(lunar_i18n.LUNAR_DAYS_I18N, {"es": {str(ld): {"title": "ES title"}}}), \
             patch.dict(lunar_i18n.MOON_SIGNS_I18N, {"es": {sign_key: {"desc": "ES sign desc"}}}):
            data = get_lunar_today_data("es")
            assert data["day_title"] == "ES title"
            assert data["sign_desc"] == "ES sign desc"


class TestLunarTodayEndpoint:
    async def test_es_lang_does_not_crash(self, client):
        res = await client.get("/v1/lunar/today?lang=es")
        assert res.status_code == 200
        assert res.json()["day_title"]  # falls back to English content, not empty

    async def test_invalid_lang_falls_back_to_english(self, client):
        res = await client.get("/v1/lunar/today?lang=xx")
        assert res.status_code == 200


class TestLunarMonthEndpoint:
    async def test_es_lang_uses_reused_sign_names(self, client):
        res = await client.get("/v1/lunar/month?lang=es")
        assert res.status_code == 200
        data = res.json()
        assert data
        assert data[0]["moon_sign"] in SIGNS  # falls back to English name, not Russian
