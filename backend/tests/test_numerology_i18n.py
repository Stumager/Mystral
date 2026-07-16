"""TZ-080: numerology.py's number meanings, karmic descriptions, Pythagoras
square cells/lines, and angel numbers were all ru/en-only (get_number_data,
pythagoras_square, and a `famous` field that was hardcoded Russian
regardless of lang — the same class of bug as runes' `deity`). Fixed via
the shared structural_i18n helpers, with English as the fallback until a
language is actually generated.
"""
from datetime import date
from unittest.mock import patch

from app.data import numerology_i18n
from app.data.numerology import (
    ANGEL_NUMBERS,
    CELL_LEVELS_EN,
    CELL_NAMES_EN,
    KARMIC_DESCRIPTIONS_EN,
    KARMIC_DESCRIPTIONS_RU,
    LINE_DEFS,
    NUMBER_DATA,
    get_number_data,
    karmic_description,
    pythagoras_square,
)


class TestFamousFieldSplit:
    def test_every_number_has_separate_ru_and_en_famous(self):
        for nd in NUMBER_DATA.values():
            assert "famous" not in nd, "still has the old combined famous field"
            assert nd["famous_ru"] and nd["famous_en"]
            assert len(nd["famous_ru"]) == len(nd["famous_en"])

    def test_famous_en_is_not_just_a_copy_of_famous_ru(self):
        for nd in NUMBER_DATA.values():
            assert nd["famous_en"] != nd["famous_ru"]


class TestGetNumberData:
    def test_ru_lang(self):
        data = get_number_data(1, "ru")
        assert data["name"] == NUMBER_DATA[1]["name_ru"]
        assert data["famous"] == NUMBER_DATA[1]["famous_ru"]

    def test_en_lang(self):
        data = get_number_data(1, "en")
        assert data["name"] == NUMBER_DATA[1]["name_en"]
        assert data["famous"] == NUMBER_DATA[1]["famous_en"]
        assert data["strengths"] == NUMBER_DATA[1]["strengths_en"]

    def test_es_falls_back_to_english_until_generated(self):
        data = get_number_data(1, "es")
        assert data["name"] == NUMBER_DATA[1]["name_en"]
        assert data["famous"] == NUMBER_DATA[1]["famous_en"]

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(numerology_i18n.NUMBER_DATA_I18N, {"es": {"1": {
            "name": "Uno-ES", "famous_0": "Napoleón Bonaparte",
        }}}):
            data = get_number_data(1, "es")
            assert data["name"] == "Uno-ES"
            # only index 0 was generated - index 1/2 fall back to English
            assert data["famous"][0] == "Napoleón Bonaparte"
            assert data["famous"][1] == NUMBER_DATA[1]["famous_en"][1]

    def test_master_numbers_still_resolve(self):
        for n in (11, 22, 33):
            assert get_number_data(n, "en")["name"] == NUMBER_DATA[n]["name_en"]

    def test_reduces_non_master_numbers(self):
        # 40 -> 4
        assert get_number_data(40, "en")["name"] == NUMBER_DATA[4]["name_en"]


class TestKarmicDescription:
    def test_ru(self):
        assert karmic_description(13, "ru") == KARMIC_DESCRIPTIONS_RU[13]

    def test_en(self):
        assert karmic_description(13, "en") == KARMIC_DESCRIPTIONS_EN[13]

    def test_es_falls_back_to_english(self):
        assert karmic_description(13, "es") == KARMIC_DESCRIPTIONS_EN[13]

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(numerology_i18n.KARMIC_I18N, {"es": {"13": {"description": "ES desc"}}}):
            assert karmic_description(13, "es") == "ES desc"


class TestPythagorasSquareI18n:
    def test_cell_names_and_levels_fall_back_to_english(self):
        sq = pythagoras_square(date(1995, 11, 8), "es")
        cell_1 = next(c for c in sq["cells"] if c["number"] == 1)
        assert cell_1["name"] == CELL_NAMES_EN[1]

    def test_line_titles_fall_back_to_english(self):
        sq = pythagoras_square(date(1995, 11, 8), "es")
        assert sq["lines"][0]["title"] == LINE_DEFS[0]["title_en"]

    def test_ru_lang_unaffected(self):
        sq = pythagoras_square(date(1995, 11, 8), "ru")
        cell_1 = next(c for c in sq["cells"] if c["number"] == 1)
        assert cell_1["name"] == "Характер и сила воли"

    def test_es_uses_i18n_once_populated(self):
        with patch.dict(numerology_i18n.CELL_NAMES_I18N, {"es": {"1": {"name": "ES name"}}}), \
             patch.dict(numerology_i18n.LINE_DEFS_I18N, {"es": {"0": {"title": "ES title"}}}):
            sq = pythagoras_square(date(1995, 11, 8), "es")
            cell_1 = next(c for c in sq["cells"] if c["number"] == 1)
            assert cell_1["name"] == "ES name"
            assert sq["lines"][0]["title"] == "ES title"


class TestAngelNumberEndpoint:
    async def test_defaults_to_russian_meaning(self, client):
        res = await client.get("/v1/numerology/angel/11:11")
        assert res.status_code == 200
        data = res.json()
        assert data["meaning"] == ANGEL_NUMBERS["11:11"]["meaning_ru"]
        # Backward-compat fields untouched.
        assert data["meaning_ru"] == ANGEL_NUMBERS["11:11"]["meaning_ru"]
        assert data["meaning_en"] == ANGEL_NUMBERS["11:11"]["meaning_en"]

    async def test_en_lang(self, client):
        res = await client.get("/v1/numerology/angel/11:11?lang=en")
        assert res.status_code == 200
        assert res.json()["meaning"] == ANGEL_NUMBERS["11:11"]["meaning_en"]

    async def test_es_falls_back_to_english_until_generated(self, client):
        res = await client.get("/v1/numerology/angel/11:11?lang=es")
        assert res.status_code == 200
        assert res.json()["meaning"] == ANGEL_NUMBERS["11:11"]["meaning_en"]

    async def test_unknown_number_404s(self, client):
        res = await client.get("/v1/numerology/angel/99:99")
        assert res.status_code == 404
