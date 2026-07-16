"""ES/PT/TR/UK card names for tarot.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n. `key`
is the string form of the 0-77 card id (0-21 major arcana, 22-77 minor
arcana in suit/rank order). Each of the 78 names is translated as a single
whole string rather than composed from separate suit+rank parts — rank/suit
word order and grammatical case vary by language (e.g. genitive constructions
in Russian/Ukrainian, "de"-phrases in Spanish/Portuguese), so a generic
template would produce incorrect minor-arcana names in several languages.

Empty until scripts/generate_structural_translations.py --section tarot
populates it; localized_field() falls back to English for any language not
present here yet.
"""

CARD_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
