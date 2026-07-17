"""TZ-080: translate structural (non-SEO) reference data into ES/PT/TR/UK.

Unlike generate_seo_translations.py (independently-authored SEO prose,
cached in a DB table, freely regenerable on a cache miss), this data is
canonical reference content — compatibility labels, rune meanings, planet
names, ... — read on every hot-path request (draw/profile/interpret), not
once on an SEO page. It must stay faithful to the existing ru/en meaning
(a rune must mean the same thing in Spanish as in Russian) rather than be
independently authored per language, and it must be committed to the repo
as importable Python, not sit in a cache that can be empty. So the prompt
always includes BOTH the ru and en reference values and asks for a faithful
*translation*, not new copy — and the output goes into
backend/app/data/<section>_i18n.py, in the {lang: {key: {field: value}}}
shape read by app.core.structural_i18n, instead of a database row.

Reuses the call/resume/backoff mechanics of generate_seo_translations.py.

Run inside the backend container (needs OPENROUTER key from env):

    docker compose exec backend python scripts/generate_structural_translations.py --section compatibility
    docker compose exec backend python scripts/generate_structural_translations.py --section compatibility --langs es --dry-run
    docker compose exec backend python scripts/generate_structural_translations.py --section runes --keys fehu,uruz --force
    docker compose exec backend python scripts/generate_structural_translations.py --retry-failed

Resumable: (lang, key, field) triples already present in the target
<section>_i18n.py are skipped, so an interrupted run can simply be
restarted. A failed item is never written there in the first place, so a
plain re-run already retries it — no separate "failed" state to track.
Rejected/failed items are listed in the final summary for a targeted
re-run via --section ... --keys, or use --retry-failed to sweep every
section's resume pass in one command once all 6 have had a first pass.
"""
import argparse
import asyncio
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Same stub as tests/conftest.py: kerykeion needs a C extension (pyswisseph)
# with no Windows wheel. natal.py imports it at module level, so importing
# the natal registry below would fail on a local Windows dev box even
# though this script never touches astro math (only the plain-dict
# PLANET_NAMES/SIGN_ORDER tables) — the real container always has it.
try:
    import kerykeion  # noqa: F401
except ImportError:
    import types

    _stub = types.ModuleType("kerykeion")

    class _StubSubject:  # pragma: no cover — never actually used here
        def __init__(self, *a, **k):
            raise RuntimeError("kerykeion stub: astro math not available in local runs")

    _stub.AstrologicalSubject = _StubSubject
    _stub.KerykeionChartSVG = _StubSubject
    sys.modules["kerykeion"] = _stub

STRUCTURAL_LANGS = ("es", "pt", "tr", "uk")  # unlike SEO's PREFIX_LANGS, "en" is never a target here

BACKOFF_STEPS = (30, 60, 120)
DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"

# (key, field, ru_value, en_value) — one entry per translatable string.
TranslationItem = tuple[str, str, str, str]


def _compatibility_registry() -> dict[str, list[TranslationItem]]:
    """Every translatable label in compatibility.py: zodiac signs, elements,
    Chinese zodiac animals, composite-chart planet names. `key` is the
    string index into the matching ru/en list, except for the planet names
    which are already keyed by planet id (e.g. "sun")."""
    from app.api.v1.compatibility import (
        CHINESE, CHINESE_RU, COMPOSITE_PLANET_NAMES, COMPOSITE_PLANET_NAMES_RU,
        ELEMENTS_EN, ELEMENTS_RU, SIGNS, SIGNS_RU,
    )
    return {
        "SIGNS_I18N": [(str(i), "name", ru, en) for i, (en, ru) in enumerate(zip(SIGNS, SIGNS_RU))],
        "ELEMENTS_I18N": [(str(i), "name", ru, en) for i, (en, ru) in enumerate(zip(ELEMENTS_EN, ELEMENTS_RU))],
        "CHINESE_I18N": [(str(i), "name", ru, en) for i, (en, ru) in enumerate(zip(CHINESE, CHINESE_RU))],
        "COMPOSITE_PLANET_NAMES_I18N": [
            (key, "name", COMPOSITE_PLANET_NAMES_RU.get(key, key), en)
            for key, en in COMPOSITE_PLANET_NAMES.items()
        ],
    }


def _tarot_registry() -> dict[str, list[TranslationItem]]:
    """All 78 tarot card names, translated as whole strings rather than
    composed from separate suit+rank parts — rank/suit word order and
    grammatical case vary by language, so a generic template would produce
    incorrect minor-arcana names in several of the 4 target languages."""
    from app.api.v1.tarot import CARD_NAMES, CARD_NAMES_RU
    return {
        "CARD_NAMES_I18N": [
            (str(cid), "name", CARD_NAMES_RU[cid], CARD_NAMES[cid])
            for cid in sorted(CARD_NAMES)
        ],
    }


def _natal_registry() -> dict[str, list[TranslationItem]]:
    """Planet names and zodiac sign names in natal.py. Aspect names
    (ASPECT_TYPES) already have ru/en from TZ-076/079 and aren't part of
    this section; the 5 long interpretation prompt templates are handled
    separately (TZ-080 Module 5)."""
    from app.api.v1.natal import PLANET_NAMES_EN, PLANET_NAMES_RU, SIGN_ORDER, SIGNS_RU
    return {
        "PLANET_NAMES_I18N": [
            (key, "name", PLANET_NAMES_RU[key], en) for key, en in PLANET_NAMES_EN.items()
        ],
        "SIGNS_I18N": [
            (sign, "name", SIGNS_RU[sign], sign) for sign in SIGN_ORDER
        ],
    }


def _numerology_registry() -> dict[str, list[TranslationItem]]:
    """Number meanings, karmic debt descriptions, Pythagoras square cell
    names/levels and line meanings, and angel number meanings. List-valued
    fields (strengths/challenges/famous) are split into indexed scalar
    items ("strengths_0", "strengths_1", ...), matching pick_list()'s
    read-side convention — the translate step only handles single strings."""
    from app.data.numerology import (
        ANGEL_NUMBERS, CELL_LEVELS_EN, CELL_LEVELS_RU, CELL_NAMES_EN, CELL_NAMES_RU,
        KARMIC_DESCRIPTIONS_EN, KARMIC_DESCRIPTIONS_RU, LINE_DEFS, NUMBER_DATA,
    )

    number_items: list[TranslationItem] = []
    for num, nd in NUMBER_DATA.items():
        key = str(num)
        for field in ("name", "title", "description", "career", "love"):
            number_items.append((key, field, nd[f"{field}_ru"], nd[f"{field}_en"]))
        for field in ("strengths", "challenges", "famous"):
            for i, (ru_v, en_v) in enumerate(zip(nd[f"{field}_ru"], nd[f"{field}_en"])):
                number_items.append((key, f"{field}_{i}", ru_v, en_v))

    return {
        "NUMBER_DATA_I18N": number_items,
        "KARMIC_I18N": [
            (str(num), "description", KARMIC_DESCRIPTIONS_RU[num], KARMIC_DESCRIPTIONS_EN[num])
            for num in KARMIC_DESCRIPTIONS_RU
        ],
        "CELL_NAMES_I18N": [
            (str(num), "name", CELL_NAMES_RU[num], CELL_NAMES_EN[num]) for num in CELL_NAMES_RU
        ],
        "CELL_LEVELS_I18N": [
            (str(num), "description", CELL_LEVELS_RU[num], CELL_LEVELS_EN[num]) for num in CELL_LEVELS_RU
        ],
        "LINE_DEFS_I18N": [
            (str(idx), field, ld[f"{field}_ru"], ld[f"{field}_en"])
            for idx, ld in enumerate(LINE_DEFS) for field in ("title", "desc")
        ],
        "ANGEL_NUMBERS_I18N": [
            (num, "meaning", entry["meaning_ru"], entry["meaning_en"])
            for num, entry in ANGEL_NUMBERS.items()
        ],
    }


_RUNE_SCALAR_FIELDS = ("name", "keyword", "meaning", "deity", "love", "career", "health", "magic", "as_amulet")


def _runes_registry() -> dict[str, list[TranslationItem]]:
    """Runes, rune spreads, and staves — this is one of the two BATCHED
    sections (see BATCHED_SECTIONS below): all fields of one rune/spread/
    stave go out in a single API call, not one call per field, since this
    section alone is ~340 individual strings. `areas` is deliberately
    excluded — it's dead data, never read by the API."""
    from app.data.runes import RUNES, SPREADS_RUNES
    from app.data.staves import STAVES

    rune_items: list[TranslationItem] = []
    for r in RUNES:
        key = r["id"]
        for field in _RUNE_SCALAR_FIELDS:
            rune_items.append((key, field, r[f"{field}_ru"], r[f"{field}_en"]))
        if r["reversed_meaning_ru"] is not None:
            rune_items.append((key, "reversed_meaning", r["reversed_meaning_ru"], r["reversed_meaning_en"]))

    spread_items: list[TranslationItem] = []
    for key, s in SPREADS_RUNES.items():
        spread_items.append((key, "name", s["name_ru"], s["name_en"]))
        spread_items.append((key, "desc", s["desc_ru"], s["desc_en"]))
        for i, (ru_v, en_v) in enumerate(zip(s["positions_ru"], s["positions_en"])):
            spread_items.append((key, f"positions_{i}", ru_v, en_v))

    stave_items: list[TranslationItem] = [
        (s["id"], field, s[f"{field}_ru"], s[f"{field}_en"])
        for s in STAVES for field in ("name", "purpose", "description", "how_to_use")
    ]

    return {
        "RUNES_I18N": rune_items,
        "SPREADS_RUNES_I18N": spread_items,
        "STAVES_I18N": stave_items,
    }


_LUNAR_DAY_SCALAR_FIELDS = ("symbol", "title", "desc", "health", "beauty", "money",
                            "love", "work", "spiritual", "dreams", "stones")
_LUNAR_DAY_LIST_FIELDS = ("favorable", "unfavorable")
_MOON_SIGN_SCALAR_FIELDS = ("desc", "work", "love", "health", "beauty")
_MOON_SIGN_LIST_FIELDS = ("favorable", "unfavorable")


def _lunar_registry() -> dict[str, list[TranslationItem]]:
    """The biggest section (~640 strings): 30 lunar days, 12 moon signs,
    6 lunar events, 8 moon phase names. Batched like runes — all fields of
    one day/sign/event go out in a single API call. The moon sign *name*
    itself isn't included here — it's the same 12 zodiac names natal.py
    already translates (natal_i18n.SIGNS_I18N), reused via
    app.api.v1.lunar._sign_name rather than translated twice."""
    from app.api.v1.lunar import EVENT_DATA, PHASE_NAMES_EN, PHASE_NAMES_RU
    from app.data.lunar_days import LUNAR_DAYS
    from app.data.moon_signs import MOON_SIGNS

    day_items: list[TranslationItem] = []
    for day_num, dd in LUNAR_DAYS.items():
        key = str(day_num)
        for field in _LUNAR_DAY_SCALAR_FIELDS:
            day_items.append((key, field, dd[f"{field}_ru"], dd[f"{field}_en"]))
        for field in _LUNAR_DAY_LIST_FIELDS:
            for i, (ru_v, en_v) in enumerate(zip(dd[f"{field}_ru"], dd[f"{field}_en"])):
                day_items.append((key, f"{field}_{i}", ru_v, en_v))

    sign_items: list[TranslationItem] = []
    for sign_key, sd in MOON_SIGNS.items():
        for field in _MOON_SIGN_SCALAR_FIELDS:
            sign_items.append((sign_key, field, sd[f"{field}_ru"], sd[f"{field}_en"]))
        for field in _MOON_SIGN_LIST_FIELDS:
            for i, (ru_v, en_v) in enumerate(zip(sd[f"{field}_ru"], sd[f"{field}_en"])):
                sign_items.append((sign_key, f"{field}_{i}", ru_v, en_v))

    event_items: list[TranslationItem] = [
        (event_key, field, ed[f"{field}_ru"], ed[f"{field}_en"])
        for event_key, ed in EVENT_DATA.items() for field in ("title", "desc")
    ]

    phase_items: list[TranslationItem] = [
        (str(i), "name", ru_name, en_name)
        for i, (ru_name, en_name) in enumerate(zip(PHASE_NAMES_RU, PHASE_NAMES_EN))
    ]

    return {
        "LUNAR_DAYS_I18N": day_items,
        "MOON_SIGNS_I18N": sign_items,
        "EVENT_DATA_I18N": event_items,
        "PHASE_NAMES_I18N": phase_items,
    }


SECTION_REGISTRY = {
    "compatibility": _compatibility_registry,
    "tarot": _tarot_registry,
    "natal": _natal_registry,
    "numerology": _numerology_registry,
    "runes": _runes_registry,
    "lunar": _lunar_registry,
}

_LANG_NAME = {"es": "Spanish", "pt": "Brazilian Portuguese", "tr": "Turkish", "uk": "Ukrainian"}

SYSTEM_TRANSLATE = (
    "You are a precise translator for the esoteric platform Mystral. Translate the given phrase "
    "faithfully into the target language, preserving its exact meaning and any established "
    "terminology. Do not add, omit, or reinterpret anything, and do not write independent new "
    "copy. Respond strictly with JSON."
)


def _build_prompt(ru_value: str, en_value: str, lang: str) -> str:
    return (
        f"Translate the following short phrase into {_LANG_NAME[lang]}, preserving its exact "
        f"meaning and terminology. This is a literal but natural-sounding translation, not new "
        f"independent text.\n"
        f'Russian original: "{ru_value}"\n'
        f'English reference: "{en_value}"\n'
        f'Respond with JSON: {{"translation": "..."}}'
    )


def _heuristic_ok(translation: str, ru_value: str, en_value: str, field: str) -> tuple[bool, str]:
    """Module 4's automatic pass: catches the two failure shapes that matter
    most for longer reference strings — a near-empty/truncated response, and
    the model just echoing the English reference back untranslated.

    Both the length-ratio and identical-to-English checks are skipped for
    <=2-word values. Two real false positives came from this same root
    cause: compatibility.SIGNS_I18N[0].name/es ("Aries" -> "Aries", flagged
    as untranslated) and compatibility.SIGNS_I18N[8].name/tr ("Sagittarius"
    -> "Yay", the correct Turkish name, flagged as "suspiciously short —
    27% of reference length"). Short reference strings are frequently
    proper nouns or established astrological terms (zodiac signs, some
    tarot/rune names), and for those a legitimate translation can be
    identical to English, or much shorter/longer than either reference, in
    either direction — length and identity just aren't signals of quality
    at that scale. Whether a given short value is actually correct isn't
    something this script can verify automatically either way, so the
    short case is accepted rather than burned on retries that would likely
    just reproduce the same (correct) answer. Longer phrases and sentences
    still get both checks — a whole description copied verbatim from
    English, or wildly the wrong length, remains a strong signal of a
    lazy/stuck translation there.

    A second, field-*name*-based exemption (not word-count-based) skips
    both checks entirely for numerology's `famous`/`famous_N` fields
    (indexed list items, e.g. "famous_2" — see pick_list()). These always
    hold a real person's name, and proper nouns generally aren't
    translated at all regardless of length — unlike zodiac signs, where
    short is the norm and a long result is suspicious, a person's name can
    legitimately be short ("Poe") or long ("Edgar Allan Poe"), so a
    word-count cutoff doesn't fit this field the way it does short
    astrological terms. Caught in production:
    numerology.NUMBER_DATA_I18N[11].famous_2 ("Edgar Allan Poe", 3 words —
    above the <=2-word threshold above) failed on es/pt/tr despite being
    the exactly correct spelling of that name in every one of those
    languages."""
    if not translation or not translation.strip():
        return False, "empty translation"
    if field == "famous" or field.startswith("famous_"):
        return True, ""
    if len(en_value.split()) <= 2:
        return True, ""
    ref_len = max(len(ru_value), len(en_value))
    if ref_len > 0:
        ratio = len(translation) / ref_len
        if ratio < 0.3:
            return False, f"suspiciously short ({ratio:.0%} of reference length)"
        if ratio > 3.0:
            return False, f"suspiciously long ({ratio:.0%} of reference length)"
    if len(en_value) > 3 and en_value.strip().lower() == translation.strip().lower():
        return False, "identical to the English reference — looks untranslated"
    return True, ""


async def _translate_one(ru_value: str, en_value: str, lang: str) -> str | None:
    from app.core.groq_client import _get_async_client
    client = _get_async_client()
    resp = await client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",
        messages=[
            {"role": "system", "content": SYSTEM_TRANSLATE},
            {"role": "user", "content": _build_prompt(ru_value, en_value, lang)},
        ],
        max_tokens=300,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or ""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        import json_repair
        parsed = json_repair.loads(raw)
    if not isinstance(parsed, dict):
        return None
    translation = parsed.get("translation")
    return translation.strip() if isinstance(translation, str) else None


# Sections large enough that one-call-per-field would mean thousands of
# round-trips (runes: ~340 items, lunar: ~640 items). Batching every field
# of one entity (e.g. all 9 fields of one rune) into a single JSON response
# cuts both cost overhead and wall-clock time roughly by the average field
# count per entity, without moving materially more tokens.
BATCHED_SECTIONS = {"runes", "lunar"}


def _build_batch_prompt(fields: dict[str, tuple[str, str]], lang: str) -> str:
    lines = [
        f'- "{field}" — Russian: "{ru_value}" | English: "{en_value}"'
        for field, (ru_value, en_value) in fields.items()
    ]
    return (
        f"Translate each of the following fields into {_LANG_NAME[lang]}, preserving each one's "
        f"exact meaning and terminology. Each field is independent — translate it on its own, do "
        f"not merge, summarize, or cross-reference fields. This is a literal but natural-sounding "
        f"translation, not new independent text.\n"
        + "\n".join(lines) +
        f'\nRespond with a single JSON object whose keys are exactly the field names above and '
        f'whose values are their translations, e.g. {{"field_name": "translation", ...}}'
    )


async def _translate_batch(fields: dict[str, tuple[str, str]], lang: str) -> dict[str, str] | None:
    from app.core.groq_client import _get_async_client
    client = _get_async_client()
    resp = await client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",
        messages=[
            {"role": "system", "content": SYSTEM_TRANSLATE},
            {"role": "user", "content": _build_batch_prompt(fields, lang)},
        ],
        max_tokens=200 * len(fields) + 200,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or ""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        import json_repair
        parsed = json_repair.loads(raw)
    if not isinstance(parsed, dict):
        return None
    return {k: v.strip() for k, v in parsed.items() if isinstance(v, str) and v.strip()}


def _default_header(section: str) -> str:
    return (
        f'"""ES/PT/TR/UK labels for {section}.py (TZ-080).\n\n'
        f"Shape: {{lang: {{key: {{field: value}}}}}} — see app.core.structural_i18n.\n"
        f"Generated by scripts/generate_structural_translations.py --section {section}.\n"
        f'"""\n\n'
    )


def _existing_header(path: Path, section: str) -> str:
    if not path.exists():
        return _default_header(section)
    text = path.read_text(encoding="utf-8")
    m = re.match(r'(""".*?"""\s*\n)', text, re.DOTALL)
    return m.group(1) if m else _default_header(section)


def _load_existing_dicts(section: str, dict_names: list[str]) -> dict[str, dict]:
    """Loads straight from the file at DATA_DIR/<section>_i18n.py, rather
    than `import app.data.<section>_i18n` — a package import would be
    cached in sys.modules and hand back a live reference into whatever the
    running process already imported, silently ignoring both a redirected
    DATA_DIR (breaks testing) and any on-disk change made since that first
    import (breaks resume within a long-lived process)."""
    empty = {lang: {} for lang in STRUCTURAL_LANGS}
    path = DATA_DIR / f"{section}_i18n.py"
    if not path.exists():
        return {name: dict(empty) for name in dict_names}
    spec = importlib.util.spec_from_file_location(f"_structural_i18n_{section}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {name: getattr(mod, name, dict(empty)) for name in dict_names}


def _write_i18n_module(section: str, dicts: dict[str, dict]) -> None:
    path = DATA_DIR / f"{section}_i18n.py"
    header = _existing_header(path, section)
    body = "\n".join(
        f"{name}: dict[str, dict[str, dict[str, str]]] = "
        + json.dumps(value, ensure_ascii=False, indent=4, sort_keys=True)
        for name, value in dicts.items()
    )
    path.write_text(header + "\n" + body + "\n", encoding="utf-8")


class _Progress:
    """Shared counters + the write-after-every-success durability rule, so
    an interrupted run loses at most one in-flight item/batch either way."""

    def __init__(self, section: str, existing: dict[str, dict]):
        self.section = section
        self.existing = existing
        self.planned = self.generated = self.skipped = 0
        self.failed: list[str] = []
        self.started = time.monotonic()

    def persist(self) -> None:
        _write_i18n_module(self.section, self.existing)

    def log_ok(self, label: str, count: int) -> None:
        self.generated += count
        elapsed = time.monotonic() - self.started
        print(f"OK {label} ({self.generated} done, {self.skipped} skipped, "
              f"{elapsed / 60:.1f} min elapsed)", flush=True)


async def _run_per_field(dict_name: str, items: list[TranslationItem], lang: str,
                         keys: list[str] | None, force: bool, delay: float,
                         dry_run: bool, section: str, progress: _Progress) -> None:
    bucket_all = progress.existing.setdefault(dict_name, {}).setdefault(lang, {})
    for key, field, ru_value, en_value in items:
        if keys and key not in keys:
            continue
        label = f"{section}.{dict_name}[{key}].{field}/{lang}"
        if key in bucket_all and field in bucket_all[key] and not force:
            progress.skipped += 1
            continue
        progress.planned += 1
        if dry_run:
            print(f"[dry-run] would translate {label}", flush=True)
            continue

        translation = None
        for attempt, backoff in enumerate((0,) + BACKOFF_STEPS):
            if backoff:
                print(f"  retry {attempt} for {label} in {backoff}s", flush=True)
                await asyncio.sleep(backoff)
            try:
                translation = await _translate_one(ru_value, en_value, lang)
            except Exception as e:  # network layers can still leak
                print(f"  error for {label}: {e}", flush=True)
                translation = None
                continue
            ok, reason = _heuristic_ok(translation or "", ru_value, en_value, field)
            if ok:
                break
            print(f"  rejected {label}: {reason} -> {translation!r}", flush=True)
            translation = None

        if translation is None:
            progress.failed.append(label)
            print(f"FAILED {label}", flush=True)
        else:
            bucket_all.setdefault(key, {})[field] = translation
            progress.persist()
            progress.log_ok(label, 1)
        if not dry_run:
            await asyncio.sleep(delay)


async def _run_batched(dict_name: str, items: list[TranslationItem], lang: str,
                       keys: list[str] | None, force: bool, delay: float,
                       dry_run: bool, section: str, progress: _Progress) -> None:
    bucket_all = progress.existing.setdefault(dict_name, {}).setdefault(lang, {})

    grouped: dict[str, dict[str, tuple[str, str]]] = {}
    for key, field, ru_value, en_value in items:
        if keys and key not in keys:
            continue
        grouped.setdefault(key, {})[field] = (ru_value, en_value)

    for key, fields in grouped.items():
        existing_entry = bucket_all.get(key, {})
        pending = {f: v for f, v in fields.items() if force or f not in existing_entry}
        progress.skipped += len(fields) - len(pending)
        if not pending:
            continue
        label = f"{section}.{dict_name}[{key}]/{lang}"
        progress.planned += len(pending)
        if dry_run:
            print(f"[dry-run] would translate {label} ({len(pending)} fields: {', '.join(pending)})", flush=True)
            continue

        succeeded: dict[str, str] = {}
        for attempt, backoff in enumerate((0,) + BACKOFF_STEPS):
            if not pending:
                break
            if backoff:
                print(f"  retry {attempt} for {label} in {backoff}s ({len(pending)} fields left)", flush=True)
                await asyncio.sleep(backoff)
            try:
                translations = await _translate_batch(pending, lang)
            except Exception as e:  # network layers can still leak
                print(f"  error for {label}: {e}", flush=True)
                translations = None
            if not translations:
                continue
            for field, (ru_value, en_value) in list(pending.items()):
                candidate = translations.get(field)
                if candidate is None:
                    continue
                ok, reason = _heuristic_ok(candidate, ru_value, en_value, field)
                if ok:
                    succeeded[field] = candidate
                    del pending[field]
                else:
                    print(f"  rejected {label}.{field}: {reason} -> {candidate!r}", flush=True)

        if succeeded:
            bucket_all.setdefault(key, {}).update(succeeded)
            progress.persist()
            progress.log_ok(f"{label} ({len(succeeded)}/{len(fields)} fields)", len(succeeded))
        for field in pending:
            progress.failed.append(f"{label}.{field}")
            print(f"FAILED {label}.{field}", flush=True)
        if not dry_run:
            await asyncio.sleep(delay)


async def run(section: str, langs: list[str], keys: list[str] | None,
              force: bool, delay: float, dry_run: bool) -> int:
    items_by_dict = SECTION_REGISTRY[section]()
    existing = _load_existing_dicts(section, list(items_by_dict.keys()))
    progress = _Progress(section, existing)
    runner = _run_batched if section in BATCHED_SECTIONS else _run_per_field

    for lang in langs:
        for dict_name, items in items_by_dict.items():
            await runner(dict_name, items, lang, keys, force, delay, dry_run, section, progress)

    print(f"\nDone: {progress.generated} generated, {progress.skipped} skipped, "
          f"{len(progress.failed)} failed (of {progress.planned} planned)", flush=True)
    if progress.failed:
        print("Failed items (re-run with --keys, or re-run the whole section):", flush=True)
        for label in progress.failed:
            print(f"  {label}", flush=True)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--section", choices=sorted(SECTION_REGISTRY),
                        help="which section to translate (required unless --retry-failed)")
    parser.add_argument("--retry-failed", action="store_true",
                        help="sweep every registered section in one command instead of one "
                             "--section at a time. A failed item is never written to its "
                             "_i18n.py module (see run()/the resume mechanism), so a plain "
                             "resume pass already retries exactly the failed/not-yet-attempted "
                             "items and leaves successful ones alone — this flag is purely a "
                             "convenience for doing that sweep across all sections at once, e.g. "
                             "once all 6 have had their first pass, instead of hunting through "
                             "each section's run log for what still needs --keys.")
    parser.add_argument("--langs", default=",".join(STRUCTURAL_LANGS),
                        help=f"comma-separated subset of: {','.join(STRUCTURAL_LANGS)}")
    parser.add_argument("--keys", default="", help="comma-separated keys to limit to (for spot-fixing)")
    parser.add_argument("--force", action="store_true", help="retranslate even if already present")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between API calls")
    parser.add_argument("--dry-run", action="store_true", help="list what would be translated, no API calls")
    args = parser.parse_args()

    if not args.retry_failed and not args.section:
        print("Either --section or --retry-failed is required")
        return 2

    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    bad = [l for l in langs if l not in STRUCTURAL_LANGS]
    if bad:
        print(f"Unknown language(s): {','.join(bad)} — valid: {','.join(STRUCTURAL_LANGS)}")
        return 2

    if not args.dry_run and not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is not set — translation would fail on every item. "
              "Run inside the backend container (docker compose exec backend ...).")
        return 2

    keys = [k.strip() for k in args.keys.split(",") if k.strip()] or None
    sections = sorted(SECTION_REGISTRY) if args.retry_failed else [args.section]

    overall = 0
    for section in sections:
        if len(sections) > 1:
            print(f"\n=== {section} ===", flush=True)
        code = asyncio.run(run(section, langs, keys, args.force, args.delay, args.dry_run))
        overall = overall or code
    return overall


if __name__ == "__main__":
    sys.exit(main())
