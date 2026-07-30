"""TZ-110: the batch SEO generation script's PAGE_TYPES tuple is a
hand-maintained copy of what seo_page_items() actually yields.

Drift here fails silently and expensively: PAGE_TYPES only gates --types, so
a page type missing from it is skipped even by a plain full run with no
flags — the pages simply never get generated in batch, and nothing reports
it. That is exactly what happened when natal_pillar/lunar_pillar were added.
"""
from app.core.seo_generator import seo_page_items
from scripts.generate_seo_translations import PAGE_TYPES


class TestPageTypesStayInSync:
    def test_every_generated_page_type_is_selectable(self):
        actual = {pt for pt, _slug, _data in seo_page_items()}
        missing = sorted(actual - set(PAGE_TYPES))
        assert not missing, (
            f"page type(s) {missing} are produced by seo_page_items() but absent from "
            f"the script's PAGE_TYPES — they would never be generated in batch"
        )

    def test_no_dead_entries(self):
        actual = {pt for pt, _slug, _data in seo_page_items()}
        stale = sorted(set(PAGE_TYPES) - actual)
        assert not stale, f"PAGE_TYPES lists {stale}, which seo_page_items() no longer yields"

    def test_the_three_pillars_are_selectable(self):
        for pt in ("natal_pillar", "lunar_pillar", "compatibility_pillar"):
            assert pt in PAGE_TYPES, pt

    def test_pillar_slugs_are_unique_across_types(self):
        # The --slugs filter is NOT type-scoped (it matches on slug alone), so
        # a pillar slug shared with another type would silently drag unrelated
        # pages into a targeted regeneration run.
        by_slug: dict[str, list[str]] = {}
        for pt, slug, _data in seo_page_items():
            by_slug.setdefault(slug, []).append(pt)
        for slug in ("natal-chart", "lunar-calendar", "compatibility"):
            assert by_slug.get(slug) and len(by_slug[slug]) == 1, (
                f"slug {slug!r} is used by {by_slug.get(slug)} — a --slugs run would hit all of them"
            )
