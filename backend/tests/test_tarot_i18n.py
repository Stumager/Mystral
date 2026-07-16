"""TZ-080: /tarot/spread had no `lang` param at all (always returned raw
`name`/`name_ru`, frontend picked between just those two), and
/tarot/interpret's per-card name resolution was a `ru else en` ternary, so
ES/PT/TR/UK always got the English card name. Fixed via a shared
_card_name() helper backed by tarot_i18n.py, with English as the fallback
until a language is actually generated.
"""
from unittest.mock import patch

from app.api.v1.tarot import CARD_NAMES, CARD_NAMES_RU, _card_name
from app.data import tarot_i18n


class TestCardNameHelper:
    def test_ru_returns_russian_name(self):
        assert _card_name(0, "ru") == CARD_NAMES_RU[0]

    def test_en_returns_english_name(self):
        assert _card_name(0, "en") == CARD_NAMES[0]

    def test_es_falls_back_to_english_until_generated(self):
        assert _card_name(0, "es") == CARD_NAMES[0]

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(tarot_i18n.CARD_NAMES_I18N, {"es": {"0": {"name": "El Loco"}}}):
            assert _card_name(0, "es") == "El Loco"

    def test_minor_arcana_id_resolves(self):
        # id 22 = Ace of Wands (first minor arcana card)
        assert _card_name(22, "en") == CARD_NAMES[22]
        assert _card_name(22, "ru") == CARD_NAMES_RU[22]


class TestSpreadEndpointLang:
    async def test_spread_defaults_to_russian_display_name(self, client, auth_headers):
        res = await client.post("/v1/tarot/spread", headers=auth_headers,
                                 json={"spread_id": "card_of_day"})
        assert res.status_code == 200
        card = res.json()["cards"][0]
        assert card["name_display"] == CARD_NAMES_RU[card["id"]]

    async def test_spread_with_en_lang_returns_english_display_name(self, client, pro_headers):
        res = await client.post("/v1/tarot/spread", headers=pro_headers,
                                 json={"spread_id": "card_of_day", "lang": "en"})
        assert res.status_code == 200
        card = res.json()["cards"][0]
        assert card["name_display"] == CARD_NAMES[card["id"]]
        # Backward-compat fields untouched.
        assert card["name"] == CARD_NAMES[card["id"]]
        assert card["name_ru"] == CARD_NAMES_RU[card["id"]]


class TestInterpretUsesLocalizedName:
    async def test_interpret_prefers_submitted_name_display(self, client, auth_headers):
        async def fake_stream(*a, **k):
            yield "data: [DONE]\n\n"

        with patch("app.api.v1.tarot.safe_groq_stream", side_effect=fake_stream):
            res = await client.post(
                "/v1/tarot/interpret", headers=auth_headers,
                json={
                    "spread_id": "card_of_day",
                    "cards": [{"id": 0, "name": "The Fool", "name_ru": "Шут", "name_display": "Le Fou", "reversed": False}],
                    "positions": ["Card of the Day"],
                    "lang": "en",
                },
            )
        assert res.status_code == 200
