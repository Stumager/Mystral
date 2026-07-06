"""TZ-037c: batch generation of translated SEO content (615 pages).

Run inside the backend container (needs DB + OPENROUTER key from env):

    docker compose exec backend python scripts/generate_seo_translations.py
    docker compose exec backend python scripts/generate_seo_translations.py --langs es --types numerology
    docker compose exec backend python scripts/generate_seo_translations.py --dry-run

Resumable: rows that already exist are skipped, so an interrupted run can
simply be restarted. Failed pages degrade to on-demand generation when the
page is first requested, and are listed in the final summary for re-runs.
"""
import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import select  # noqa: E402

from app.core.database import get_session_context  # noqa: E402
from app.core.seo_generator import _generate_and_store, localize_data, seo_page_items  # noqa: E402
from app.data.seo_i18n import PREFIX_LANGS  # noqa: E402
from app.models.user import SeoContent  # noqa: E402

PAGE_TYPES = ("zodiac", "tarot", "rune", "numerology")
BACKOFF_STEPS = (30, 60, 120)


async def run(langs: list[str], types: list[str], slugs: list[str] | None,
              force: bool, delay: float, dry_run: bool) -> int:
    # no-op when tables already exist (prod); makes local scratch runs work
    from sqlmodel import SQLModel
    from app.core.database import engine
    import app.models  # noqa: F401 — register table classes
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    items = [(pt, slug, data) for pt, slug, data in seo_page_items()
             if pt in types and (not slugs or slug in slugs)]
    total = len(items) * len(langs)
    print(f"Plan: {len(items)} pages x {len(langs)} langs = {total} generations", flush=True)

    generated = skipped = 0
    failed: list[str] = []
    started = time.monotonic()

    for lang in langs:
        for i, (ptype, slug, data) in enumerate(items):
            label = f"{ptype}/{slug}/{lang}"
            async with get_session_context() as session:
                result = await session.exec(
                    select(SeoContent).where(
                        SeoContent.page_type == ptype,
                        SeoContent.slug == slug,
                        SeoContent.lang == lang,
                    )
                )
                existing = result.first()
                if existing and not force:
                    skipped += 1
                    continue
                if dry_run:
                    print(f"[dry-run] would generate {label}", flush=True)
                    generated += 1
                    continue
                if existing and force:
                    await session.delete(existing)
                    await session.commit()

                content = None
                for attempt, backoff in enumerate((0,) + BACKOFF_STEPS):
                    if backoff:
                        print(f"  retry {attempt} for {label} in {backoff}s", flush=True)
                        await asyncio.sleep(backoff)
                    try:
                        content = await _generate_and_store(
                            ptype, slug, localize_data(ptype, data, lang), session, lang,
                        )
                    except Exception as e:  # network layers can still leak
                        print(f"  error for {label}: {e}", flush=True)
                        content = None
                        continue
                    if content and not content.get("_fallback"):
                        break
                    content = None

                if content is None:
                    failed.append(label)
                    print(f"FAILED {label}", flush=True)
                else:
                    generated += 1
                    elapsed = time.monotonic() - started
                    print(f"OK {label} ({generated} done, {skipped} skipped, "
                          f"{elapsed / 60:.1f} min elapsed)", flush=True)
            if not dry_run:
                await asyncio.sleep(delay)

    print(f"\nDone: {generated} generated, {skipped} skipped, {len(failed)} failed", flush=True)
    if failed:
        print("Failed pages (re-run with --slugs, or let on-demand generation pick them up):", flush=True)
        for label in failed:
            print(f"  {label}", flush=True)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--langs", default=",".join(PREFIX_LANGS),
                        help=f"comma-separated subset of: {','.join(PREFIX_LANGS)}")
    parser.add_argument("--types", default=",".join(PAGE_TYPES),
                        help=f"comma-separated subset of: {','.join(PAGE_TYPES)}")
    parser.add_argument("--slugs", default="", help="comma-separated slugs to limit to")
    parser.add_argument("--force", action="store_true", help="regenerate even if a row exists")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between API calls")
    parser.add_argument("--dry-run", action="store_true", help="list what would be generated")
    args = parser.parse_args()

    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    bad = [l for l in langs if l not in PREFIX_LANGS]
    if bad:
        print(f"Unknown language(s): {','.join(bad)} — valid: {','.join(PREFIX_LANGS)} "
              f"(note: Ukrainian is 'uk', not 'ua')")
        return 2

    types = [t.strip() for t in args.types.split(",") if t.strip()]
    bad = [t for t in types if t not in PAGE_TYPES]
    if bad:
        print(f"Unknown page type(s): {','.join(bad)} — valid: {','.join(PAGE_TYPES)}")
        return 2

    if not args.dry_run and not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is not set — generation would fail on every page. "
              "Run inside the backend container (docker compose exec backend ...).")
        return 2

    slugs = [s.strip() for s in args.slugs.split(",") if s.strip()] or None
    return asyncio.run(run(langs, types, slugs, args.force, args.delay, args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
