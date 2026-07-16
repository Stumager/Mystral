"""ES/PT/TR/UK content for lunar_days.py / moon_signs.py / api/v1/lunar.py
(TZ-080) — the biggest of the 6 sections (~640 translatable strings).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
- LUNAR_DAYS_I18N: key is str(1-30); fields are symbol, title, desc, health,
  beauty, money, love, work, spiritual, dreams, stones, and indexed list
  items favorable_0.., unfavorable_0...
- MOON_SIGNS_I18N: key is the English sign name (e.g. "Aries"); fields are
  desc, work, love, health, beauty, and indexed list items favorable_0..,
  unfavorable_0... The sign *name* itself is NOT duplicated here — it's the
  same 12 zodiac names already covered by natal_i18n.SIGNS_I18N, reused via
  app.data.natal_i18n to avoid translating the same word twice.
- EVENT_DATA_I18N: key is the event type (e.g. "new_moon"); fields are
  title, desc.
- PHASE_NAMES_I18N: key is str(0-7); field is "name".

Generated in batches by scripts/generate_structural_translations.py
--section lunar (all fields of one day/sign/event in a single API call —
see BATCHED_SECTIONS). Empty until that runs; pick()/pick_list() fall back
to English for any language not present here yet.
"""

LUNAR_DAYS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
MOON_SIGNS_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
EVENT_DATA_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
PHASE_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {"es": {}, "pt": {}, "tr": {}, "uk": {}}
