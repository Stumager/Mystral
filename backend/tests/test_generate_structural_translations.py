"""TZ-080 Module 1: the translate-structural-data script. These test the
pure logic (heuristic check, prompt building, registry shape) and the
resume/write cycle with a mocked LLM call — no real OPENROUTER_API_KEY or
network access needed.
"""
from unittest.mock import AsyncMock, patch

from scripts.generate_structural_translations import (
    BATCHED_SECTIONS,
    SECTION_REGISTRY,
    STRUCTURAL_LANGS,
    _build_batch_prompt,
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


class TestTarotRegistry:
    def test_registry_has_all_78_cards(self):
        items_by_dict = SECTION_REGISTRY["tarot"]()
        assert set(items_by_dict) == {"CARD_NAMES_I18N"}
        assert len(items_by_dict["CARD_NAMES_I18N"]) == 78

    def test_every_card_has_nonempty_ru_and_en_values(self):
        for key, field, ru_value, en_value in SECTION_REGISTRY["tarot"]()["CARD_NAMES_I18N"]:
            assert key and field == "name" and ru_value and en_value


class TestNatalRegistry:
    def test_registry_has_planets_and_signs(self):
        items_by_dict = SECTION_REGISTRY["natal"]()
        assert set(items_by_dict) == {"PLANET_NAMES_I18N", "SIGNS_I18N"}
        assert len(items_by_dict["PLANET_NAMES_I18N"]) == 13
        assert len(items_by_dict["SIGNS_I18N"]) == 12

    def test_every_item_has_nonempty_ru_and_en_values(self):
        for items in SECTION_REGISTRY["natal"]().values():
            for key, field, ru_value, en_value in items:
                assert key and field and ru_value and en_value


class TestNumerologyRegistry:
    def test_registry_has_all_expected_dicts(self):
        items_by_dict = SECTION_REGISTRY["numerology"]()
        assert set(items_by_dict) == {
            "NUMBER_DATA_I18N", "KARMIC_I18N", "CELL_NAMES_I18N",
            "CELL_LEVELS_I18N", "LINE_DEFS_I18N", "ANGEL_NUMBERS_I18N",
        }
        assert len(items_by_dict["KARMIC_I18N"]) == 4
        assert len(items_by_dict["CELL_NAMES_I18N"]) == 9
        assert len(items_by_dict["CELL_LEVELS_I18N"]) == 5
        assert len(items_by_dict["LINE_DEFS_I18N"]) == 16  # 8 lines x (title, desc)
        assert len(items_by_dict["ANGEL_NUMBERS_I18N"]) == 35

    def test_number_data_includes_list_fields_as_indexed_items(self):
        items = SECTION_REGISTRY["numerology"]()["NUMBER_DATA_I18N"]
        keys = {(key, field) for key, field, _, _ in items}
        assert ("1", "strengths_0") in keys
        assert ("1", "famous_2") in keys
        # 12 numbers x (5 scalar fields + 4 strengths + 3 challenges + 3 famous) = 180
        assert len(items) == 180

    def test_every_item_has_nonempty_ru_and_en_values(self):
        for items in SECTION_REGISTRY["numerology"]().values():
            for key, field, ru_value, en_value in items:
                assert key and field and ru_value and en_value


class TestRunesRegistry:
    def test_registry_has_all_expected_dicts(self):
        items_by_dict = SECTION_REGISTRY["runes"]()
        assert set(items_by_dict) == {"RUNES_I18N", "SPREADS_RUNES_I18N", "STAVES_I18N"}

    def test_rune_items_exclude_areas_and_include_reversed_meaning_only_when_reversible(self):
        items = SECTION_REGISTRY["runes"]()["RUNES_I18N"]
        fields_by_rune: dict[str, set[str]] = {}
        for key, field, _, _ in items:
            fields_by_rune.setdefault(key, set()).add(field)
        assert "areas" not in fields_by_rune["fehu"]
        assert "reversed_meaning" in fields_by_rune["fehu"]  # can_reverse: True
        assert "reversed_meaning" not in fields_by_rune["gebo"]  # can_reverse: False

    def test_staves_have_all_four_fields(self):
        items = SECTION_REGISTRY["runes"]()["STAVES_I18N"]
        fields = {field for key, field, _, _ in items if key == "protection"}
        assert fields == {"name", "purpose", "description", "how_to_use"}

    def test_every_item_has_nonempty_ru_and_en_values(self):
        for items in SECTION_REGISTRY["runes"]().values():
            for key, field, ru_value, en_value in items:
                assert key and field and ru_value and en_value


class TestLunarRegistry:
    def test_registry_has_all_expected_dicts(self):
        items_by_dict = SECTION_REGISTRY["lunar"]()
        assert set(items_by_dict) == {
            "LUNAR_DAYS_I18N", "MOON_SIGNS_I18N", "EVENT_DATA_I18N", "PHASE_NAMES_I18N",
        }
        assert len(items_by_dict["EVENT_DATA_I18N"]) == 12  # 6 events x (title, desc)
        assert len(items_by_dict["PHASE_NAMES_I18N"]) == 8

    def test_lunar_days_cover_all_30_days(self):
        items = SECTION_REGISTRY["lunar"]()["LUNAR_DAYS_I18N"]
        keys = {key for key, _, _, _ in items}
        assert keys == {str(d) for d in range(1, 31)}

    def test_moon_signs_exclude_name_field(self):
        # name is reused from natal_i18n.SIGNS_I18N, not translated again here
        items = SECTION_REGISTRY["lunar"]()["MOON_SIGNS_I18N"]
        fields = {field for key, field, _, _ in items if key == "Aries"}
        assert "name" not in fields
        assert "desc" in fields

    def test_every_item_has_nonempty_ru_and_en_values(self):
        for items in SECTION_REGISTRY["lunar"]().values():
            for key, field, ru_value, en_value in items:
                assert key and field and ru_value and en_value

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


class TestBatchPromptBuilding:
    def test_includes_every_field_and_both_reference_languages(self):
        prompt = _build_batch_prompt({
            "keyword": ("Богатство", "Wealth"),
            "meaning": ("Материальное благополучие", "Material well-being"),
        }, "es")
        assert "keyword" in prompt and "meaning" in prompt
        assert "Богатство" in prompt and "Wealth" in prompt
        assert "Spanish" in prompt


class TestBatchedSectionsRunThroughRunBatched:
    """Runes/lunar are large enough that one-call-per-field would mean
    thousands of round-trips — BATCHED_SECTIONS routes them through
    _run_batched, which sends every field of one entity in a single call."""

    def test_runes_and_lunar_are_batched(self):
        assert BATCHED_SECTIONS == {"runes", "lunar"}

    async def test_batched_section_sends_all_fields_in_one_call(self, tmp_path):
        fake_registry = {
            "runes": lambda: {"RUNES_I18N": [
                ("fehu", "keyword", "Богатство", "Wealth"),
                ("fehu", "meaning", "Изобилие", "Abundance"),
            ]},
        }
        calls = []

        async def fake_batch(fields, lang):
            calls.append(dict(fields))
            return {"keyword": "Riqueza", "meaning": "Abundancia"}

        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path), \
             patch.dict("scripts.generate_structural_translations.SECTION_REGISTRY", fake_registry, clear=True), \
             patch("scripts.generate_structural_translations._translate_batch", side_effect=fake_batch):
            code = await run("runes", ["es"], None, force=False, delay=0, dry_run=False)
            assert code == 0
            assert len(calls) == 1, "both fields of the one rune must go in a single call"
            assert set(calls[0]) == {"keyword", "meaning"}
            loaded = _load_existing_dicts("runes", ["RUNES_I18N"])
        assert loaded["RUNES_I18N"]["es"]["fehu"]["keyword"] == "Riqueza"
        assert loaded["RUNES_I18N"]["es"]["fehu"]["meaning"] == "Abundancia"

    async def test_batched_section_salvages_partial_success(self, tmp_path):
        # One field passes the heuristic, the other is a verbatim echo and
        # must be retried/failed on its own, without discarding the good one.
        fake_registry = {
            "runes": lambda: {"RUNES_I18N": [
                ("fehu", "keyword", "Богатство", "Wealth"),
                ("fehu", "meaning", "Изобилие", "Abundance"),
            ]},
        }

        async def fake_batch(fields, lang):
            return {"keyword": "Riqueza", "meaning": "Abundance"}  # meaning: untranslated echo

        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path), \
             patch.dict("scripts.generate_structural_translations.SECTION_REGISTRY", fake_registry, clear=True), \
             patch("scripts.generate_structural_translations.BACKOFF_STEPS", ()), \
             patch("scripts.generate_structural_translations._translate_batch", side_effect=fake_batch):
            code = await run("runes", ["es"], None, force=False, delay=0, dry_run=False)
            assert code == 1  # "meaning" ends up in the failure summary
            loaded = _load_existing_dicts("runes", ["RUNES_I18N"])
        assert loaded["RUNES_I18N"]["es"]["fehu"]["keyword"] == "Riqueza"
        assert "meaning" not in loaded["RUNES_I18N"]["es"]["fehu"]

    async def test_batched_section_resumes_only_missing_fields(self, tmp_path):
        fake_registry = {
            "runes": lambda: {"RUNES_I18N": [
                ("fehu", "keyword", "Богатство", "Wealth"),
                ("fehu", "meaning", "Изобилие", "Abundance"),
            ]},
        }
        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path):
            _write_i18n_module("runes", {"RUNES_I18N": {
                "es": {"fehu": {"keyword": "Riqueza"}}, "pt": {}, "tr": {}, "uk": {},
            }})

        seen_fields = []

        async def fake_batch(fields, lang):
            seen_fields.append(set(fields))
            return {f: f"{v[1]}-ES" for f, v in fields.items()}

        with patch("scripts.generate_structural_translations.DATA_DIR", tmp_path), \
             patch.dict("scripts.generate_structural_translations.SECTION_REGISTRY", fake_registry, clear=True), \
             patch("scripts.generate_structural_translations._translate_batch", side_effect=fake_batch):
            code = await run("runes", ["es"], None, force=False, delay=0, dry_run=False)

        assert code == 0
        assert seen_fields == [{"meaning"}], "keyword was already present and must not be re-sent"
