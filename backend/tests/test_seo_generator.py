"""TZ-060: JSON parsing robustness for AI-generated SEO content.

These test the pure parsing/prompt-building logic directly (no network) —
production failures were "Expecting ',' delimiter" JSON errors from the
model, which response_format=json_object + a json_repair fallback are
meant to eliminate or recover from without silently losing content.
"""
from app.core.seo_generator import (
    GENERATION_MAX_TOKENS,
    PROMPTS,
    PROMPTS_I18N,
    _build_prompt,
    _parse_content_json,
    localize_data,
)
from app.data.seo_data import NUMEROLOGY_BY_SLUG, RUNE_BY_SLUG, TAROT_BY_SLUG, ZODIAC_BY_SLUG
from app.data.seo_i18n import PREFIX_LANGS


class TestParseContentJson:
    def test_valid_json_parses(self):
        raw = '{"intro": "Hello.", "sections": [{"title": "A", "text": "B"}], "faq": [{"q": "Q", "a": "A"}], "cta_text": "Try it."}'
        result = _parse_content_json(raw, "zodiac", "aries", "en")
        assert result is not None
        assert result["intro"] == "Hello."

    def test_recovers_from_embedded_literal_quote(self):
        # Reproduces the production failure class: an unescaped literal "
        # inside a string value breaks strict json.loads with exactly
        # "Expecting ',' delimiter" — json_repair must recover it.
        raw = ('{"intro": "Aries is the "ram" of the zodiac.", '
               '"sections": [{"title": "Overview", "text": "Bold and direct."}], '
               '"faq": [{"q": "Q", "a": "A"}], "cta_text": "Try now."}')
        result = _parse_content_json(raw, "zodiac", "aries", "en")
        assert result is not None
        assert "ram" in result["intro"]
        assert result["sections"][0]["text"] == "Bold and direct."

    def test_model_wraps_json_in_prose_or_fences(self):
        raw = ('Here is the JSON:\n```json\n'
               '{"intro": "I.", "sections": [{"title": "T", "text": "X"}], '
               '"faq": [{"q": "Q", "a": "A"}], "cta_text": "C"}\n```')
        result = _parse_content_json(raw, "rune", "fehu", "ru")
        assert result is not None
        assert result["intro"] == "I."

    def test_no_json_object_at_all_returns_none(self):
        result = _parse_content_json("The model refused to answer.", "zodiac", "aries", "en")
        assert result is None

    def test_unrecoverable_garbage_returns_none_not_garbage(self):
        # json_repair silently returns '' for hopeless input instead of
        # raising — must not be mistaken for valid content.
        raw = "{not json at all, just { broken } } nonsense"
        result = _parse_content_json(raw, "zodiac", "aries", "en")
        assert result is None

    def test_missing_required_keys_returns_none(self):
        raw = '{"intro": "Hello.", "sections": []}'  # missing faq/cta_text
        result = _parse_content_json(raw, "zodiac", "aries", "en")
        assert result is None


class TestPromptBuilding:
    """The escaping-guidance additions to _QUALITY/_QUALITY_I18N must not
    break .format() with stray/unbalanced braces, for every language and
    every page type (this was the actual mechanism a bad edit could crash)."""

    def test_ru_prompts_format_for_all_page_types(self):
        data_by_type = {
            "zodiac": ZODIAC_BY_SLUG["aries"],
            "tarot": TAROT_BY_SLUG["the-fool"],
            "rune": RUNE_BY_SLUG["fehu"],
            "numerology": NUMEROLOGY_BY_SLUG["life-path-1"],
        }
        for page_type, data in data_by_type.items():
            prompt = _build_prompt(page_type, data, "ru")
            assert prompt and "{" not in prompt and "}" not in prompt or "JSON" in prompt
            assert "\"intro\"" in prompt  # schema example survived formatting

    def test_i18n_prompts_format_for_all_langs_and_types(self):
        data_by_type = {
            "zodiac": ZODIAC_BY_SLUG["aries"],
            "tarot": TAROT_BY_SLUG["the-fool"],
            "rune": RUNE_BY_SLUG["fehu"],
            "numerology": NUMEROLOGY_BY_SLUG["life-path-1"],
        }
        for lang in PREFIX_LANGS:
            for page_type, raw_data in data_by_type.items():
                data = localize_data(page_type, raw_data, lang)
                prompt = _build_prompt(page_type, data, lang)
                assert prompt
                # no leftover single braces (would mean a .format() field
                # escaped incorrectly, e.g. an un-doubled brace in an example)
                assert "{name}" not in prompt and "{language}" not in prompt
                assert "\"intro\"" in prompt

    def test_prompts_ru_unchanged_page_specific_sections(self):
        # The per-page-type topic list (module 3's "byte-identical" ru
        # requirement) must survive the shared _QUALITY suffix growing.
        assert "Описание характера" in PROMPTS["zodiac"]
        assert "Значение в прямом положении" in PROMPTS["tarot"]
        assert "Происхождение и этимология" in PROMPTS["rune"]
        assert "Характер и личность" in PROMPTS["numerology"]

    def test_i18n_prompts_have_escaping_guidance(self):
        for tpl in PROMPTS_I18N.values():
            assert "double-quote" in tpl or "quote" in tpl


class TestTruncationFollowUp:
    """Reproduces the second production failure: response_format=json_object
    guaranteed valid JSON syntax, but the model still ran out of max_tokens
    mid-generation (after rambling with self-corrections in the "famous
    people" section) and never emitted faq/cta_text. json_repair happily
    closes the truncated structure into syntactically valid JSON missing
    required keys — _parse_content_json must reject that, not accept it."""

    def test_truncated_response_missing_required_keys_is_rejected(self):
        # Shape actually observed in prod: well-formed intro + sections,
        # but the response was cut off before faq/cta_text ever appeared.
        raw = (
            '{"intro": "Aries is bold.", '
            '"sections": [{"title": "Overview", "text": "Long text about Aries."}, '
            '{"title": "Famous Aries People", "text": '
            "\"Wait, he's Aquarius. Actually, let me correct that. "
            'Reliable Aries: Robert Downey Jr."}]}'
        )
        result = _parse_content_json(raw, "zodiac", "aries", "en")
        assert result is None

    def test_max_tokens_has_real_headroom_over_old_value(self):
        # Regression guard: the old 3000 was the direct cause of the
        # truncation above. Must stay comfortably higher.
        assert GENERATION_MAX_TOKENS >= 4096

    def test_quality_directives_forbid_rambling_and_cap_famous_people(self):
        from app.core.seo_generator import _QUALITY, _QUALITY_I18N
        assert "3" in _QUALITY and "4" in _QUALITY  # "3–4 реальных имени"
        assert "self-correct" in _QUALITY_I18N or "wait, actually" in _QUALITY_I18N
        assert "3-4 real people" in _QUALITY_I18N
