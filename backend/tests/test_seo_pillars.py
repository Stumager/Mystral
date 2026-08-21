"""TZ-110: the three pillar landings (/natal-chart, /lunar-calendar,
/compatibility) as real product pages — home icon, hero art, result preview,
FAQ, glossary CTA into the app, departure animation.

base.html is shared by all 17 SEO templates, so roughly half of these tests
assert the *absence* of the new chrome everywhere outside the three pages the
ticket scopes: the section hubs and leaf pages must render exactly as before.
"""
import json
import re
import xml.etree.ElementTree as ET

import pytest
from markupsafe import escape

from app.data.seo_i18n import PREFIX_LANGS, UI


def _esc(s: str) -> str:
    """Jinja autoescapes, so a localized string containing an apostrophe —
    Turkish "Ay'ın Çağrısı", Ukrainian "з'єднані" — reaches the HTML as
    &#39;. Compare against the escaped form, not the raw dict value."""
    return str(escape(s))

# path, section, deep link, CTA i18n key, hero alt i18n key
PILLARS = [
    ("/natal-chart", "natal", "/app/natal", "pillar_cta_natal", "hero_natal_alt"),
    ("/lunar-calendar", "lunar", "/app/lunar", "pillar_cta_lunar", "hero_lunar_alt"),
    ("/compatibility", "compat", "/app/compatibility", "pillar_cta_compat", "hero_compat_alt"),
    ("/destiny-matrix", "matrix", "/app/matrix", "pillar_cta_matrix", "hero_matrix_alt"),
]
PILLAR_PATHS = [p[0] for p in PILLARS]
ALL_LANGS = ("ru",) + PREFIX_LANGS

NON_PILLAR_PATHS = [
    "/zodiac", "/tarot", "/runes", "/zodiac/leo", "/tarot/the-fool", "/runes/fehu",
    "/numerology/life-path-1", "/lunar-calendar/day/1", "/natal-chart/planets/sun",
    "/natal-chart/houses/1", "/natal-chart/ascendant", "/compatibility/aries",
    "/destiny-matrix/arcana/1",
]


def _url(lang: str, path: str) -> str:
    return path if lang == "ru" else f"/{lang}{path}"


class TestPillarHomeIcon:
    """п.1 — an icon button back to mystral.space/. The wordmark and the
    "Home" text link already pointed there, but neither reads as a button on
    a phone, which is what the ticket asks for."""

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_pillar_has_home_icon_button(self, client, path):
        res = await client.get(path)
        assert res.status_code == 200
        assert '<a href="/" class="hdr-home"' in res.text, path

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_home_icon_label_is_localized(self, client, lang, path):
        res = await client.get(_url(lang, path))
        assert f'aria-label="{_esc(UI[lang]["home_icon_title"])}"' in res.text, (lang, path)

    @pytest.mark.parametrize("path", NON_PILLAR_PATHS)
    async def test_non_pillar_pages_have_no_home_icon(self, client, path):
        res = await client.get(path)
        assert res.status_code == 200
        assert "hdr-home" not in res.text, path

    @pytest.mark.parametrize("path", PILLAR_PATHS + ["/tarot/the-fool", "/zodiac"])
    async def test_wordmark_still_links_home_everywhere(self, client, path):
        res = await client.get(path)
        assert '<a href="/" class="hdr-logo">MYSTRAL</a>' in res.text, path


class TestPillarHeroAndPreview:
    """п.2 — gold line-art hero plus a badged example of the actual result."""

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    async def test_hero_art_is_inlined_with_a_localized_label(self, client, path, section, href, cta_key, alt_key):
        res = await client.get(path)
        assert 'class="hero-art"' in res.text
        assert 'class="mx-art"' in res.text, "hero SVG must be inline, not an extra request"
        assert f'aria-label="{_esc(UI["ru"][alt_key])}"' in res.text

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_preview_block_is_badged_as_an_example(self, client, path):
        res = await client.get(path)
        assert 'class="preview"' in res.text, path
        # The figures shown are illustrative — it must never read as real data.
        assert f'<span class="badge">{_esc(UI["ru"]["preview_badge"])}</span>' in res.text, path

    async def test_natal_preview_shows_example_placements(self, client):
        res = await client.get("/natal-chart")
        assert "Дом Карьеры" in res.text and "Дом Семьи" in res.text
        assert "Асцендент" in res.text

    async def test_lunar_preview_uses_real_curated_day_data(self, client):
        # Day 11's favourable list is curated data (lunar_days.py), not LLM
        # output — the preview shows something true even with generation off.
        res = await client.get("/lunar-calendar")
        assert '<div class="pv-day-n">11</div>' in res.text
        assert 'class="pv-tag"' in res.text

    async def test_compat_preview_shows_the_pair_drawn_in_the_hero(self, client):
        res = await client.get("/compatibility")
        assert "Лев" in res.text and "Весы" in res.text
        assert 'class="bar-fill"' in res.text

    async def test_matrix_preview_shows_the_cross_checked_example_date(self, client):
        # TZ-101's verified example (15.05.1990: core=6, personality=15,
        # talents=5 — cross-checked against an independent calculator, see
        # PROGRESS.md) computed live via app.data.destiny_matrix.calculate(),
        # not a hand-typed illustration.
        res = await client.get("/destiny-matrix")
        assert "Точка опоры" in res.text
        from app.data.destiny_matrix import arcana_name
        assert arcana_name(6, "ru") in res.text
        assert arcana_name(15, "ru") in res.text
        assert arcana_name(5, "ru") in res.text

    @pytest.mark.parametrize("path", NON_PILLAR_PATHS)
    async def test_non_pillar_pages_get_no_hero_or_preview(self, client, path):
        res = await client.get(path)
        assert "hero-art" not in res.text, path
        assert 'class="preview"' not in res.text, path

    def test_every_hero_svg_is_wellformed_xml(self):
        from app.data.seo_art import HERO_SVG
        assert set(HERO_SVG) == {"natal", "lunar", "compat", "matrix"}
        for section, svg in HERO_SVG.items():
            ET.fromstring(svg)  # raises on malformed markup
            assert 'aria-hidden="true"' in svg, section

    def test_hero_art_is_deterministic(self):
        # Rebuilt art must be byte-identical across processes, or every
        # response would differ and caching/ETags would stop meaning anything.
        from app.data.seo_art import (
            _build_compat_rings, _build_lunar_circle, _build_matrix_octagram, _build_natal_wheel,
        )
        assert _build_natal_wheel() == _build_natal_wheel()
        assert _build_lunar_circle() == _build_lunar_circle()
        assert _build_compat_rings() == _build_compat_rings()
        assert _build_matrix_octagram() == _build_matrix_octagram()


class TestPillarFaq:
    """п.3 — the same FAQ pattern the tarot/rune cards use: a visible block
    plus FAQPage structured data. /natal-chart and /lunar-calendar had
    neither before, because they had no generated content at all."""

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_faq_block_is_rendered(self, client, path):
        res = await client.get(path)
        assert _esc(UI["ru"]["faq_title"]) in res.text, path
        assert 'class="faq-q"' in res.text and 'class="faq-a"' in res.text, path

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_faqpage_jsonld_is_emitted(self, client, path):
        res = await client.get(path)
        assert '"@type":"FAQPage"' in res.text, path
        assert '"acceptedAnswer"' in res.text, path

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_structured_data_blocks_are_valid_json(self, client, path):
        res = await client.get(path)
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', res.text, re.S)
        assert len(blocks) == 3, f"{path}: expected Article + FAQPage + BreadcrumbList, got {len(blocks)}"
        for b in blocks:
            json.loads(b)  # raises if a template edit broke the JSON

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_faq_present_on_every_language_version(self, client, lang, path):
        res = await client.get(_url(lang, path))
        assert res.status_code == 200
        assert '"@type":"FAQPage"' in res.text


class TestPillarAppCta:
    """п.5 — an esoteric-named button deep-linking into /app/{section} via the
    TZ-096 mechanism. Calculation and payment stay inside the app; the landing
    itself never touches the authenticated backend."""

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    async def test_cta_uses_the_glossary_name(self, client, path, section, href, cta_key, alt_key):
        res = await client.get(path)
        assert _esc(UI["ru"][cta_key]) in res.text, path

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    async def test_cta_points_at_the_app_deep_link(self, client, path, section, href, cta_key, alt_key):
        res = await client.get(path)
        assert f'<a href="{href}" class="app-cta" data-veil>' in res.text, path

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    async def test_closing_cta_also_targets_the_app(self, client, path, section, href, cta_key, alt_key):
        res = await client.get(path)
        assert f'<a href="{href}" class="cta-btn" data-veil>' in res.text, path

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    @pytest.mark.parametrize("lang", PREFIX_LANGS)
    async def test_deep_link_is_never_language_prefixed(self, client, lang, path, section, href, cta_key, alt_key):
        # nginx's SEO regex has no "app" alternative, so "/es/app/natal" would
        # be served index.html and then resolve to "home" — App.tsx's
        # pageFromPath only matches ^/app/…. The link carries the section, not
        # the language; the SPA keeps its own language state.
        res = await client.get(_url(lang, path))
        assert f'href="{href}"' in res.text, (lang, path)
        assert f"/{lang}/app/" not in res.text, (lang, path)

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    @pytest.mark.parametrize("lang", PREFIX_LANGS)
    async def test_cta_label_is_localized(self, client, lang, path, section, href, cta_key, alt_key):
        res = await client.get(_url(lang, path))
        assert _esc(UI[lang][cta_key]) in res.text, (lang, path)

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_page_makes_no_authenticated_backend_calls(self, client, path):
        res = await client.get(path)
        assert "/v1/" not in res.text, path
        assert "fetch(" not in res.text, path
        assert "XMLHttpRequest" not in res.text, path
        assert "Authorization" not in res.text, path


class TestPillarTransitionVeil:
    """п.6 — a branded ~1.15s dissolve on the way into the app, not a loading
    spinner, and strictly progressive enhancement."""

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_veil_markup_and_script_are_present(self, client, path):
        res = await client.get(path)
        assert 'id="mx-veil"' in res.text, path
        assert 'class="mx-spark"' in res.text, path
        assert "a[data-veil]" in res.text, path

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_reduced_motion_is_honoured_in_both_css_and_js(self, client, path):
        res = await client.get(path)
        assert "prefers-reduced-motion: reduce" in res.text, path  # the JS guard
        assert "prefers-reduced-motion:reduce" in res.text, path   # the CSS guard

    @pytest.mark.parametrize("path,section,href,cta_key,alt_key", PILLARS)
    async def test_cta_still_navigates_without_javascript(self, client, path, section, href, cta_key, alt_key):
        # The veil intercepts the click; with JS off the CTA must remain an
        # ordinary link to the same place, never a button or a "#" stub.
        res = await client.get(path)
        assert f'href="{href}"' in res.text
        assert 'href="#"' not in res.text

    @pytest.mark.parametrize("path", NON_PILLAR_PATHS)
    async def test_non_pillar_pages_carry_no_veil(self, client, path):
        res = await client.get(path)
        assert "mx-veil" not in res.text, path
        assert "data-veil" not in res.text, path


class TestPillarGlossaryOnPage:
    """п.4 — no "AI"/"ИИ"/"интеграция" anywhere on these three pages. This
    covers the page chrome; generated copy is guarded separately by
    seo_generator._has_tech_vocabulary (see test_seo_generator.py)."""

    BANNED_PHRASES = ("искусственный интеллект", "нейросет", "интеграц", "інтеграц",
                      "artificial intelligence", "neural network", "yapay zeka")

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_no_technical_vocabulary_in_the_rendered_page(self, client, lang, path):
        res = await client.get(_url(lang, path))
        assert res.status_code == 200
        assert not re.search(r"\bAI\b", res.text), (lang, path)
        assert not re.search(r"\bИИ\b", res.text), (lang, path)
        low = res.text.lower()
        for banned in self.BANNED_PHRASES:
            assert banned not in low, (lang, path, banned)


class TestPillarRegressionOnOtherPages:
    """The ticket leaves the section hubs and leaf pages alone. base.html is
    shared by all 17 templates, so its edits must be inert wherever the new
    blocks are not filled in."""

    async def test_zodiac_cta_still_points_at_natal_chart(self, client):
        # TZ-085's behaviour, unaffected by the new conditional data-veil.
        res = await client.get("/zodiac/scorpio")
        assert '<a href="/natal-chart" class="cta-btn">' in res.text

    @pytest.mark.parametrize("path", ["/tarot/the-fool", "/runes/fehu", "/numerology/life-path-1"])
    async def test_other_ctas_still_point_at_the_homepage(self, client, path):
        res = await client.get(path)
        assert '<a href="/" class="cta-btn">' in res.text, path

    @pytest.mark.parametrize("path", NON_PILLAR_PATHS)
    async def test_pillar_stylesheet_does_not_leak(self, client, path):
        res = await client.get(path)
        assert ".app-cta" not in res.text, path
        assert "mx-spin-slow" not in res.text, path

    async def test_hub_without_generated_content_stays_indexable(self, client):
        res = await client.get("/es/zodiac")
        assert 'content="index, follow"' in res.text

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    async def test_pillar_fallback_content_is_noindex(self, client, path):
        # GROQ_API_KEY is empty under test, so content is the fallback. All
        # three pillars generate now, so all three must noindex when they
        # cannot — /compatibility already behaved this way before TZ-110.
        res = await client.get(f"/es{path}")
        assert 'content="noindex, follow"' in res.text, path

    @pytest.mark.parametrize("path", PILLAR_PATHS)
    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_pillar_canonical_and_hreflang_unchanged(self, client, lang, path):
        res = await client.get(_url(lang, path))
        assert f'<link rel="canonical" href="https://mystral.space{_url(lang, path)}">' in res.text
        assert 'hreflang="x-default"' in res.text
