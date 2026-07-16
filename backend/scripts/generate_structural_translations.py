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

Resumable: (lang, key, field) triples already present in the target
<section>_i18n.py are skipped, so an interrupted run can simply be
restarted. Rejected/failed items are listed in the final summary for
re-runs via --keys.
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


# Extend with "tarot", "natal", "numerology", "runes", "lunar" as each
# section gets wired up to read from its own <section>_i18n.py module.
SECTION_REGISTRY = {
    "compatibility": _compatibility_registry,
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


def _heuristic_ok(translation: str, ru_value: str, en_value: str) -> tuple[bool, str]:
    """Module 4's automatic pass: catches the two failure shapes that matter
    most for short reference strings — a near-empty/truncated response, and
    the model just echoing the English reference back untranslated. Proper
    names (rune/card names) are expected to resemble the English spelling,
    so this only flags a *verbatim* copy of the whole reference, not shared
    substrings."""
    if not translation or not translation.strip():
        return False, "empty translation"
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


async def run(section: str, langs: list[str], keys: list[str] | None,
              force: bool, delay: float, dry_run: bool) -> int:
    items_by_dict = SECTION_REGISTRY[section]()
    existing = _load_existing_dicts(section, list(items_by_dict.keys()))

    planned = generated = skipped = 0
    failed: list[str] = []
    started = time.monotonic()

    for lang in langs:
        for dict_name, items in items_by_dict.items():
            for key, field, ru_value, en_value in items:
                if keys and key not in keys:
                    continue
                label = f"{section}.{dict_name}[{key}].{field}/{lang}"
                bucket = existing.setdefault(dict_name, {}).setdefault(lang, {})
                if key in bucket and field in bucket[key] and not force:
                    skipped += 1
                    continue
                planned += 1
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
                    ok, reason = _heuristic_ok(translation or "", ru_value, en_value)
                    if ok:
                        break
                    print(f"  rejected {label}: {reason} -> {translation!r}", flush=True)
                    translation = None

                if translation is None:
                    failed.append(label)
                    print(f"FAILED {label}", flush=True)
                else:
                    bucket.setdefault(key, {})[field] = translation
                    # Persist after every success (not just at the end) so an
                    # interrupted run loses at most one in-flight item.
                    _write_i18n_module(section, existing)
                    generated += 1
                    elapsed = time.monotonic() - started
                    print(f"OK {label} ({generated} done, {skipped} skipped, "
                          f"{elapsed / 60:.1f} min elapsed)", flush=True)
                if not dry_run:
                    await asyncio.sleep(delay)

    print(f"\nDone: {generated} generated, {skipped} skipped, {len(failed)} failed (of {planned} planned)", flush=True)
    if failed:
        print("Failed items (re-run with --keys, or re-run the whole section):", flush=True)
        for label in failed:
            print(f"  {label}", flush=True)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--section", required=True, choices=sorted(SECTION_REGISTRY),
                        help="which section to translate")
    parser.add_argument("--langs", default=",".join(STRUCTURAL_LANGS),
                        help=f"comma-separated subset of: {','.join(STRUCTURAL_LANGS)}")
    parser.add_argument("--keys", default="", help="comma-separated keys to limit to (for spot-fixing)")
    parser.add_argument("--force", action="store_true", help="retranslate even if already present")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between API calls")
    parser.add_argument("--dry-run", action="store_true", help="list what would be translated, no API calls")
    args = parser.parse_args()

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
    return asyncio.run(run(args.section, langs, keys, args.force, args.delay, args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
