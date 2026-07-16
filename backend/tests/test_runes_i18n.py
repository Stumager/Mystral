"""TZ-080: the `deity` field in RUNES was hardcoded as a single ru/en
slash-joined string ("Фрейя / Freya") and served as-is regardless of `lang` —
an English or any other interface user still saw the Russian name first.
Fixed by splitting it into deity_ru/deity_en, same shape as every other
bilingual field on a rune (name, keyword, meaning, ...), and selecting by
language in _rune_out()."""
from app.api.v1.runes import _rune_out
from app.data.runes import RUNES


class TestDeityFieldSplit:
    def test_every_rune_has_separate_ru_and_en_deity(self):
        for rune in RUNES:
            assert "deity" not in rune, f"{rune['id']} still has the old combined deity field"
            assert rune["deity_ru"], f"{rune['id']} missing deity_ru"
            assert rune["deity_en"], f"{rune['id']} missing deity_en"

    def test_no_leftover_slash_join_artifact(self):
        # Reproduces the original bug shape directly: neither half should
        # still contain the " / " separator from the old combined string.
        for rune in RUNES:
            assert " / " not in rune["deity_ru"]
            assert " / " not in rune["deity_en"]


class TestRuneOutDeityLanguage:
    def test_ru_lang_returns_russian_deity(self):
        fehu = next(r for r in RUNES if r["id"] == "fehu")
        out = _rune_out(fehu, "ru")
        assert out["deity"] == "Фрейя"

    def test_en_lang_returns_english_deity(self):
        fehu = next(r for r in RUNES if r["id"] == "fehu")
        out = _rune_out(fehu, "en")
        assert out["deity"] == "Freya"
