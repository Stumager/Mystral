"""TZ-111: basic E-E-A-T trust signals — an /about page (who's behind
Mystral, what the calculations are based on), visible footer contacts/
requisites site-wide, and a one-line methodology disclosure on the three
pillar landings from TZ-110.

"метод Ладини", named in the ticket as the Destiny Matrix source, does not
appear anywhere in this repo (PROGRESS.md, PROGRESS_ARCHIVE.md, code) — the
only documented methodology is the TZ-101 cross-check against lady.mail.ru,
numefy.ru, and two independent GitHub implementations. about.html and these
tests are built around that real, verifiable methodology instead.
"""
import re

import pytest
from markupsafe import escape

from app.data.seo_i18n import PREFIX_LANGS, UI

ALL_LANGS = ("ru",) + PREFIX_LANGS
PILLAR_PATHS = ["/natal-chart", "/lunar-calendar", "/compatibility"]
LEGAL_EMAIL = "sasha.nechunaev1234@gmail.com"
LEGAL_INN = "230307450300"


def _esc(s: str) -> str:
    """Jinja autoescapes, so a localized string containing an apostrophe —
    Turkish "Ay'ın Çağrısı" — reaches the HTML as &#39;. Compare against the
    escaped form, not the raw dict value."""
    return str(escape(s))


def _url(lang: str, path: str) -> str:
    return path if lang == "ru" else f"/{lang}{path}"


class TestAboutPageRenders:
    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_about_page_200_on_every_language(self, client, lang):
        res = await client.get(_url(lang, "/about"))
        assert res.status_code == 200, lang
        assert res.headers["content-type"].startswith("text/html")

    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_about_is_indexable_not_a_fallback(self, client, lang):
        res = await client.get(_url(lang, "/about"))
        assert '<meta name="robots" content="index, follow">' in res.text, lang

    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_h1_and_title_are_localized(self, client, lang):
        res = await client.get(_url(lang, "/about"))
        t = UI[lang]
        assert f"<h1>{_esc(t['about_h1'])}</h1>" in res.text, lang
        assert f"<title>{_esc(t['about_title'])}</title>" in res.text, lang

    async def test_breadcrumb_schema_present(self, client):
        res = await client.get("/about")
        assert '"@type":"BreadcrumbList"' in res.text
        assert '"@type":"AboutPage"' in res.text
        assert '"@type":"Organization"' in res.text


class TestAboutContentIsHonest:
    """The page must state real, checkable facts — not invent a source name
    that isn't documented anywhere else in the project."""

    async def test_no_fabricated_ladini_attribution(self, client):
        res = await client.get("/about")
        assert "ладини" not in res.text.lower()
        assert "ladini" not in res.text.lower()

    async def test_operator_legal_identity_present(self, client):
        res = await client.get("/about")
        assert "Нечунаев" in res.text
        assert LEGAL_INN in res.text

    async def test_contact_email_present(self, client):
        res = await client.get("/about")
        assert f'href="mailto:{LEGAL_EMAIL}"' in res.text

    async def test_swiss_ephemeris_named_for_natal_method(self, client):
        res = await client.get("/about")
        assert "Swiss Ephemeris" in res.text

    async def test_destiny_matrix_cross_check_is_mentioned(self, client):
        res = await client.get("/about")
        assert "Матриц" in res.text

    async def test_links_to_privacy_and_terms(self, client):
        res = await client.get("/about")
        assert 'href="/privacy"' in res.text
        assert 'href="/terms"' in res.text


class TestFooterTrustSignalsSiteWide:
    """п.2 — footer contacts/requisites, on every SEO page, not just the
    three pillars (the footer in base.html is shared by all 17 templates)."""

    # "/" is the frontend SPA homepage, not a seo_pages.py template — the
    # backend test client 404s on it, same as every other non-SEO path.
    PAGES = ["/zodiac", "/tarot/the-fool", "/natal-chart", "/lunar-calendar",
             "/compatibility", "/runes/fehu", "/numerology/life-path-1", "/about",
             "/destiny-matrix", "/destiny-matrix/arcana/1"]

    @pytest.mark.parametrize("path", PAGES)
    async def test_footer_links_to_about_privacy_terms(self, client, path):
        res = await client.get(path)
        assert res.status_code == 200, path
        assert 'class="ft-links"' in res.text, path
        assert re.search(r'href="/?about"', res.text) or "/about" in res.text, path
        assert 'href="/privacy"' in res.text, path
        assert 'href="/terms"' in res.text, path

    @pytest.mark.parametrize("path", PAGES)
    async def test_footer_shows_legal_identity_and_email(self, client, path):
        res = await client.get(path)
        assert "Нечунаев" in res.text, path
        assert LEGAL_INN in res.text, path
        assert f'href="mailto:{LEGAL_EMAIL}"' in res.text, path

    @pytest.mark.parametrize("lang", ALL_LANGS)
    async def test_footer_about_link_is_language_prefixed(self, client, lang):
        res = await client.get(_url(lang, "/zodiac"))
        prefix = "" if lang == "ru" else f"/{lang}"
        assert f'href="{prefix}/about"' in res.text, lang


class TestPillarMethodNotes:
    """п.3 — a short, honest methodology line on each pillar page, linking
    to /about."""

    NOTES = [
        ("/natal-chart", "method_note_natal"),
        ("/lunar-calendar", "method_note_lunar"),
        ("/compatibility", "method_note_compat"),
        ("/destiny-matrix", "method_note_matrix"),
    ]

    @pytest.mark.parametrize("path,key", NOTES)
    async def test_method_note_text_present(self, client, path, key):
        res = await client.get(path)
        assert _esc(UI["ru"][key]) in res.text, path

    @pytest.mark.parametrize("path,key", NOTES)
    async def test_method_note_links_to_about(self, client, path, key):
        res = await client.get(path)
        assert '<p class="method-note">' in res.text
        assert f'href="/about">{_esc(UI["ru"]["method_note_more"])}</a>' in res.text, path

    @pytest.mark.parametrize("path", ["/zodiac", "/tarot/the-fool", "/runes/fehu"])
    async def test_non_pillar_pages_have_no_method_note(self, client, path):
        res = await client.get(path)
        assert "method-note" not in res.text, path


class TestNginxRoutesAbout:
    """Regression guard for the exact class of bug already hit three times
    this project (TZ-096 deep-link prefix, TZ-110's batch-script PAGE_TYPES,
    TZ-111's own /about): a new SEO path silently falls through to the SPA
    in production unless nginx's routing regex is updated too. TZ-113 adds
    /destiny-matrix into the SAME test rather than a parallel one-off check,
    so the next new pillar just extends SLUGS below."""

    # Every top-level SEO section slug that must resolve to the backend, not
    # the frontend SPA's location / fallback. Parametrized (not one slug per
    # test method) so a future addition is a one-line list edit, not a new
    # copy-pasted test.
    SLUGS = ["zodiac", "tarot", "runes", "numerology", "natal-chart",
             "lunar-calendar", "compatibility", "about", "destiny-matrix"]

    @pytest.mark.parametrize("slug", SLUGS)
    def test_slug_is_in_the_backend_routing_regex(self, slug):
        import pathlib
        conf = pathlib.Path(__file__).resolve().parents[2] / "nginx" / "nginx.prod.conf"
        text = conf.read_text(encoding="utf-8")
        m = re.search(r"location ~ \^/\(\(en\|es\|pt\|tr\|uk\)/\)\?\(([^)]+)\)", text)
        assert m, "could not find the SEO backend-routing regex in nginx.prod.conf"
        alternatives = m.group(1).split("|")
        assert slug in alternatives, slug


class TestSitemapIncludesAbout:
    async def test_about_url_present_for_every_language(self, client):
        res = await client.get("/sitemap.xml")
        assert res.status_code == 200
        for lang in ALL_LANGS:
            prefix = "" if lang == "ru" else f"/{lang}"
            assert f"<loc>https://mystral.space{prefix}/about</loc>" in res.text, lang
