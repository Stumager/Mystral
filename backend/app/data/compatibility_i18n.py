"""ES/PT/TR/UK labels for compatibility.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n. `key` is
the string index into the matching ru/en list (e.g. SIGNS_I18N["es"]["3"] is
the Spanish name for SIGNS[3]/SIGNS_RU[3]) for the parallel-list sections, or
the planet key (e.g. "sun") for COMPOSITE_PLANET_NAMES_I18N.

Empty until scripts/generate_structural_translations.py --section
compatibility populates it; pick()/localized_field() fall back to English
for any language not present here yet.
"""

SIGNS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
ELEMENTS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
CHINESE_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
COMPOSITE_PLANET_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
