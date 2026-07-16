"""TZ-080 Module 1: the translate-structural-data script. These test the
pure logic (heuristic check, prompt building, registry shape) and the
resume/write cycle with a mocked LLM call — no real OPENROUTER_API_KEY or
network access needed.
"""
from unittest.mock import AsyncMock, patch

from scripts.generate_structural_translations import (
    SECTION_REGISTRY,
    STRUCTURAL_LANGS,
    _build_prompt,
    _heuristic_ok,
    _load_existing_dicts,
    _write_i18n_module,
    run,
)


class TestHeuristicCheck:
    def test_empty_translation_rejected(self):
        ok, reason = _heuristic_ok("", "Овен", "Aries")
        assert not ok and "empty" in reason

    def test_reasonable_translation_accepted(self):
        ok, _ = _heuristic_ok("Aries-ES", "Овен", "Aries")
        assert ok

    def test_suspiciously_short_rejected(self):
        ok, reason = _heuristic_ok("A", "Совместимость гармоничной пары полная", "Full harmonious pair compatibility")
        assert not ok and "short" in reason

    def test_suspiciously_long_rejected(self):
        long_text = "x" * 200
        ok, reason = _heuristic_ok(long_text, "Овен", "Aries")
        assert not ok and "long" in reason

    def test_verbatim_english_echo_rejected(self):
        ok, reason = _heuristic_ok("Aries", "Овен", "Aries")
        assert not ok and "untranslated" in reason

    def test_verbatim_echo_is_case_insensitive(self):
        ok, _ = _heuristic_ok("ARIES", "Овен", "Aries")
        assert not ok

    def test_short_proper_noun_resembling_english_is_fine(self):
        # Proper names (rune ids, card names) legitimately look similar to
        # the English spelling in many languages - only an exact match is
        # flagged, not "merely similar".
        ok, _ = _heuristic_ok("Ares", "Овен", "Aries")
        assert ok


class TestBuildPrompt:
    def test_includes_both_reference_languages_and_target(self):
        prompt = _build_prompt("Овен", "Aries", "es")
        assert "Овен" in prompt
        assert "Aries" in prompt
        assert "Spanish" in prompt

    def test_all_structural_langs_have_a_display_name(self):
        for lang in STRUCTURAL_LANGS:
            prompt = _build_prompt("x", "y", lang)
            assert prompt  # raises KeyError before returning if _LANG_NAME is missing an entry


class TestCompatibilityRegistry:
    def test_registry_has_expected_dicts_and_nonzero_items(self):
        items_by_dict = SECTION_REGISTRY["compatibility"]()
        assert set(items_by_dict) == {
            "SIGNS_I18N", "ELEMENTS_I18N", "CHINESE_I18N", "COMPOSITE_PLANET_NAMES_I18N",
        }
        assert len(items_by_dict["SIGNS_I18N"]) == 12
        assert len(items_by_dict["ELEMENTS_I18N"]) == 4
        assert len(items_by_dict["CHINESE_I18N"]) == 12
        assert len(items_by_dict["COMPOSITE_PLANET_NAMES_I18N"]) == 10

    def test_every_item_has_nonempty_ru_and_en_values(self):
        items_by_dict = SECTION_REGISTRY["compatibility"]()
        for items in items_by_dict.values():
            for key, field, ru_value, en_value in items:
                assert key and field and ru_value and en_value


class TestWriteAndResumeCycle:
    """Round-trips a fake section through _write_i18n_module /
    _load_existing_dicts, and drives run() end-to-end with the LLM call
    mocked, to prove: a successful translation gets written, a second run
    skips it (resume), and --force regenerates it."""

    def test_write_then_load_round_trips(self, tmp_path):
        full = {"es": {"0": {"name": "Uno"}}, "pt": {}, "tr": {}, "uk": {}}
        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path):
            _write_i18n_module("fake", {"X_I18N": full})
            loaded = _load_existing_dicts("fake", ["X_I18N"])
        assert loaded["X_I18N"]["es"]["0"]["name"] == "Uno"
        assert loaded["X_I18N"]["pt"] == {}

    def test_load_backfills_missing_dict_name_with_empty_langs(self, tmp_path):
        # A dict_name the file doesn't define at all (e.g. a brand-new
        # translatable dict added to a section after its _i18n.py already
        # exists) must come back as {lang: {}} per STRUCTURAL_LANGS, not KeyError.
        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path):
            _write_i18n_module("fake", {"X_I18N": {"es": {}, "pt": {}, "tr": {}, "uk": {}}})
            loaded = _load_existing_dicts("fake", ["X_I18N", "Y_I18N"])
        assert loaded["Y_I18N"] == {"es": {}, "pt": {}, "tr": {}, "uk": {}}

    async def test_run_writes_translations_and_resumes_on_second_call(self, tmp_path):
        fake_registry = {
            "compatibility": lambda: {"SIGNS_I18N": [("0", "name", "Овен", "Aries")]},
        }
        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path), \
             patch.dict("scripts.generate_structural_translations.SECTION_REGISTRY", fake_registry, clear=True), \
             patch("scripts.generate_structural_translations._translate_one",
                   new=AsyncMock(return_value="Carnero")):
            code = await run("compatibility", ["es"], None, force=False, delay=0, dry_run=False)
            assert code == 0
            loaded = _load_existing_dicts("compatibility", ["SIGNS_I18N"])
            assert loaded["SIGNS_I18N"]["es"]["0"]["name"] == "Carnero"

            # Second run: already present, must be skipped (no LLM call).
            with patch("scripts.generate_structural_translations._translate_one",
                       new=AsyncMock(side_effect=AssertionError("should not be called"))):
                code2 = await run("compatibility", ["es"], None, force=False, delay=0, dry_run=False)
            assert code2 == 0

    async def test_run_reports_failure_when_heuristic_never_passes(self, tmp_path):
        fake_registry = {
            "compatibility": lambda: {"SIGNS_I18N": [("0", "name", "Овен", "Aries")]},
        }
        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path), \
             patch.dict("scripts.generate_structural_translations.SECTION_REGISTRY", fake_registry, clear=True), \
             patch("scripts.generate_structural_translations.BACKOFF_STEPS", ()), \
             patch("scripts.generate_structural_translations._translate_one",
                   new=AsyncMock(return_value="Aries")):  # verbatim echo -> always rejected
            code = await run("compatibility", ["es"], None, force=False, delay=0, dry_run=False)
        assert code == 1
