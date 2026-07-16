"""ES/PT/TR/UK content for runes.py / staves.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
- RUNES_I18N: key is the rune id (e.g. "fehu"); fields are name, keyword,
  meaning, reversed_meaning (only for runes where can_reverse is true),
  deity, love, career, health, magic, as_amulet.
- SPREADS_RUNES_I18N: key is the spread id (e.g. "rune_of_day"); fields are
  name, desc, and indexed position items ("positions_0", "positions_1", ...).
- STAVES_I18N: key is the stave id; fields are name, purpose, description,
  how_to_use.

`areas` (RUNES) is deliberately not covered here — it's never read by the
API (dead data), so translating it would be pure cost with no user-visible
effect.

Generated in batches by scripts/generate_structural_translations.py
--section runes (all fields of one rune/spread/stave in a single API call,
not one call per field — see BATCHED_SECTIONS in that script). Empty until
that runs; pick()/pick_list() fall back to English for any language not
present here yet.
"""

RUNES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
SPREADS_RUNES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
STAVES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
