"""ES/PT/TR/UK content for numerology.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
- NUMBER_DATA_I18N: key is str(number) (e.g. "1", "11", "22"); list fields
  (strengths/challenges/famous) are stored as indexed scalar items
  ("strengths_0", "strengths_1", ...) — see pick_list().
- KARMIC_I18N: key is str(karmic number) (13/14/16/19), field "description".
- CELL_NAMES_I18N / CELL_LEVELS_I18N: key is str(0-9), field "name"/"description".
- LINE_DEFS_I18N: key is str(index into LINE_DEFS), fields "title"/"desc".
- ANGEL_NUMBERS_I18N: key is the angel number string (e.g. "11:11"), field "meaning".

Empty until scripts/generate_structural_translations.py --section numerology
populates it; localized_field()/pick()/pick_list() fall back to English for
any language not present here yet.
"""

NUMBER_DATA_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
KARMIC_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
CELL_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
CELL_LEVELS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
LINE_DEFS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
ANGEL_NUMBERS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
