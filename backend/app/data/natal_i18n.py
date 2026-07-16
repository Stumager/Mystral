"""ES/PT/TR/UK names for natal.py (TZ-080): planets and zodiac signs.

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
PLANET_NAMES_I18N is keyed by planet key (e.g. "sun", "true_node");
SIGNS_I18N is keyed by the normalized English sign name (e.g. "Aries").

Scope note: aspect names (ASPECT_TYPES) already have ru/en from TZ-076/079
and the 5 long natal interpretation prompt templates (SECTION_PROMPTS_RU/EN)
are handled separately (TZ-080 Module 5) — this module only covers the
short planet/sign labels.

Empty until scripts/generate_structural_translations.py --section natal
populates it; localized_field() falls back to English for any language not
present here yet.
"""

PLANET_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
SIGNS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
