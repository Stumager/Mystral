import re
import types
from unittest.mock import AsyncMock, patch

import pytest

from app.data.seo_data import LUNAR_DAY_SEO, NATAL_PLANETS, NUMEROLOGY_SEO, RUNE_SEO
from app.data.seo_i18n import PREFIX_LANGS


class TestZodiacPages:
    async def test_zodiac_sign_returns_html(self, client):
        res = await client.get("/zodiac/scorpio")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/html")

    async def test_zodiac_sign_has_h1(self, client):
        res = await client.get("/zodiac/scorpio")
        assert "<h1" in res.text

    async def test_zodiac_sign_has_title(self, client):
        res = await client.get("/zodiac/scorpio")
        m = re.search(r"<title>([^<]+)</title>", res.text)
        assert m and len(m.group(1).strip()) > 10

    async def test_zodiac_sign_has_canonical(self, client):
        res = await client.get("/zodiac/scorpio")
        assert 'rel="canonical"' in res.text
        assert "https://mystral.space/zodiac/scorpio" in res.text

    async def test_zodiac_invalid_slug(self, client):
        res = await client.get("/zodiac/dragonborn")
        assert res.status_code == 404

    async def test_zodiac_traversal_slug(self, client):
        res = await client.get("/zodiac/..%2F..%2Fetc%2Fpasswd")
        assert res.status_code == 404

    async def test_zodiac_hub(self, client):
        res = await client.get("/zodiac")
        assert res.status_code == 200

    async def test_constellation_svg(self, client):
        res = await client.get("/zodiac/scorpio/constellation.svg")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("image/svg")


class TestTarotPages:
    async def test_tarot_card_returns_html(self, client):
        res = await client.get("/tarot/the-fool")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/html")

    async def test_tarot_invalid_slug(self, client):
        res = await client.get("/tarot/the-hacker")
        assert res.status_code == 404

    async def test_tarot_hub(self, client):
        res = await client.get("/tarot")
        assert res.status_code == 200


class TestRunePages:
    async def test_rune_returns_html(self, client):
        res = await client.get("/runes/fehu")
        assert res.status_code == 200

    async def test_rune_invalid_slug(self, client):
        res = await client.get("/runes/notarune")
        assert res.status_code == 404


class TestNatalChartPages:
    async def test_natal_planet_returns_html(self, client):
        res = await client.get("/natal-chart/planets/sun")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/html")

    async def test_natal_planet_has_h1(self, client):
        res = await client.get("/natal-chart/planets/sun")
        assert "<h1" in res.text

    async def test_natal_planet_has_canonical(self, client):
        res = await client.get("/natal-chart/planets/sun")
        assert 'rel="canonical"' in res.text
        assert "https://mystral.space/natal-chart/planets/sun" in res.text

    async def test_natal_planet_invalid_slug(self, client):
        res = await client.get("/natal-chart/planets/xenu")
        assert res.status_code == 404

    async def test_natal_planet_traversal_slug(self, client):
        res = await client.get("/natal-chart/planets/..%2F..%2Fetc%2Fpasswd")
        assert res.status_code == 404

    async def test_natal_chart_hub(self, client):
        res = await client.get("/natal-chart")
        assert res.status_code == 200


class TestLunarCalendarPages:
    async def test_lunar_day_returns_html(self, client):
        res = await client.get("/lunar-calendar/day/1")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/html")

    async def test_lunar_day_has_h1(self, client):
        res = await client.get("/lunar-calendar/day/1")
        assert "<h1" in res.text

    async def test_lunar_day_has_canonical(self, client):
        res = await client.get("/lunar-calendar/day/1")
        assert 'rel="canonical"' in res.text
        assert "https://mystral.space/lunar-calendar/day/1" in res.text

    async def test_lunar_day_invalid_slug(self, client):
        res = await client.get("/lunar-calendar/day/99")
        assert res.status_code == 404

    async def test_lunar_day_traversal_slug(self, client):
        res = await client.get("/lunar-calendar/day/..%2F..%2Fetc%2Fpasswd")
        assert res.status_code == 404

    async def test_lunar_calendar_hub(self, client):
        res = await client.get("/lunar-calendar")
        assert res.status_code == 200

    async def test_lunar_day_shows_real_curated_data(self, client):
        # unlike other sections, lunar days carry real curated data
        # (favorable/unfavorable/stones) independent of LLM generation.
        res = await client.get("/lunar-calendar/day/1")
        assert "Планирование" in res.text  # LUNAR_DAYS[1]["favorable_ru"][0]
        assert "Лунный камень" in res.text  # LUNAR_DAYS[1]["stones_ru"]


class TestAllRunesAndNumerologyPages:
    """TZ-073 regression: a SEO crawler found 21/123 pages returning 500 —
    12/24 runes and 9/9 numerology pages — because a real fixture only
    exercised one example slug per page type (test_rune_returns_html above),
    so the other slugs' behavior had never actually been asserted. Walk the
    full slug lists instead of a sample, on ru and every prefixed language,
    so a future regression can't hide behind an untested slug again."""

    @pytest.mark.parametrize("rune", RUNE_SEO, ids=lambda r: r["slug"])
    async def test_every_rune_slug_ru(self, client, rune):
        res = await client.get(f"/runes/{rune['slug']}")
        assert res.status_code == 200, f"/runes/{rune['slug']} -> {res.status_code}"

    @pytest.mark.parametrize("num", NUMEROLOGY_SEO, ids=lambda n: n["slug"])
    async def test_every_numerology_slug_ru(self, client, num):
        res = await client.get(f"/numerology/{num['slug']}")
        assert res.status_code == 200, f"/numerology/{num['slug']} -> {res.status_code}"

    @pytest.mark.parametrize("lang", PREFIX_LANGS)
    @pytest.mark.parametrize("rune", RUNE_SEO, ids=lambda r: r["slug"])
    async def test_every_rune_slug_all_langs(self, client, lang, rune):
        res = await client.get(f"/{lang}/runes/{rune['slug']}")
        assert res.status_code == 200, f"/{lang}/runes/{rune['slug']} -> {res.status_code}"

    @pytest.mark.parametrize("lang", PREFIX_LANGS)
    @pytest.mark.parametrize("num", NUMEROLOGY_SEO, ids=lambda n: n["slug"])
    async def test_every_numerology_slug_all_langs(self, client, lang, num):
        res = await client.get(f"/{lang}/numerology/{num['slug']}")
        assert res.status_code == 200, f"/{lang}/numerology/{num['slug']} -> {res.status_code}"


class TestAllNatalPlanetsAndLunarDaysPages:
    """TZ-083, following the exact precedent TZ-073/TZ-082 established for
    runes/numerology: walk every slug, not a sample, on ru and every
    prefixed language, so a regression can't hide behind an untested slug."""

    @pytest.mark.parametrize("planet", NATAL_PLANETS, ids=lambda p: p["slug"])
    async def test_every_natal_planet_slug_ru(self, client, planet):
        res = await client.get(f"/natal-chart/planets/{planet['slug']}")
        assert res.status_code == 200, f"/natal-chart/planets/{planet['slug']} -> {res.status_code}"

    @pytest.mark.parametrize("day", LUNAR_DAY_SEO, ids=lambda d: d["slug"])
    async def test_every_lunar_day_slug_ru(self, client, day):
        res = await client.get(f"/lunar-calendar/day/{day['slug']}")
        assert res.status_code == 200, f"/lunar-calendar/day/{day['slug']} -> {res.status_code}"

    @pytest.mark.parametrize("lang", PREFIX_LANGS)
    @pytest.mark.parametrize("planet", NATAL_PLANETS, ids=lambda p: p["slug"])
    async def test_every_natal_planet_slug_all_langs(self, client, lang, planet):
        res = await client.get(f"/{lang}/natal-chart/planets/{planet['slug']}")
        assert res.status_code == 200, f"/{lang}/natal-chart/planets/{planet['slug']} -> {res.status_code}"

    @pytest.mark.parametrize("lang", PREFIX_LANGS)
    @pytest.mark.parametrize("day", LUNAR_DAY_SEO, ids=lambda d: d["slug"])
    async def test_every_lunar_day_slug_all_langs(self, client, lang, day):
        res = await client.get(f"/{lang}/lunar-calendar/day/{day['slug']}")
        assert res.status_code == 200, f"/{lang}/lunar-calendar/day/{day['slug']} -> {res.status_code}"


def _fake_llm_response(payload: str):
    msg = types.SimpleNamespace(content=payload)
    choice = types.SimpleNamespace(message=msg, finish_reason="stop")
    return types.SimpleNamespace(choices=[choice])


class TestSeoContentPersistenceFailureDoesNotCrashPage:
    """TZ-073 root cause: _generate_and_store's DB-persistence step used to
    sit outside any try/except, so a transient DB failure while caching
    freshly generated content (pool exhaustion, dropped connection, etc.)
    propagated as an unhandled exception -> 500, even though the LLM had
    already produced valid content. The page must still render."""

    async def test_page_renders_even_if_caching_the_content_fails(self, client):
        good_json = (
            '{"intro": "test intro", "sections": [{"title": "t", "text": "x"}], '
            '"faq": [{"q": "q", "a": "a"}], "cta_text": "cta"}'
        )
        fake_client = types.SimpleNamespace(
            chat=types.SimpleNamespace(completions=types.SimpleNamespace(
                create=AsyncMock(return_value=_fake_llm_response(good_json))
            ))
        )
        with patch("app.core.groq_client._get_async_client", return_value=fake_client), \
             patch("sqlmodel.ext.asyncio.session.AsyncSession.commit",
                   AsyncMock(side_effect=RuntimeError("simulated transient DB error"))):
            res = await client.get("/runes/eihwaz")
        assert res.status_code == 200
        assert "test intro" in res.text


class TestSeoContentCacheLookupFailureDoesNotCrashPage:
    """TZ-082 root cause: get_seo_content's initial cache-lookup SELECT sat
    outside any try/except. The sibling read+write pair inside
    _generate_and_store got this protection in TZ-073 for the exact same
    failure class (transient DB hiccup -> unhandled 500 despite the LLM
    having produced valid content) — this first read, run before we even
    know if it's a cache hit or miss, was the one call site TZ-073 missed."""

    async def test_page_renders_even_if_cache_lookup_fails(self, client):
        good_json = (
            '{"intro": "test intro", "sections": [{"title": "t", "text": "x"}], '
            '"faq": [{"q": "q", "a": "a"}], "cta_text": "cta"}'
        )
        fake_client = types.SimpleNamespace(
            chat=types.SimpleNamespace(completions=types.SimpleNamespace(
                create=AsyncMock(return_value=_fake_llm_response(good_json))
            ))
        )
        with patch("app.core.groq_client._get_async_client", return_value=fake_client), \
             patch("sqlmodel.ext.asyncio.session.AsyncSession.exec",
                   AsyncMock(side_effect=RuntimeError("simulated transient DB error"))):
            res = await client.get("/numerology/life-path-1")
        assert res.status_code == 200
        assert "test intro" in res.text


class TestSitemap:
    async def test_sitemap_returns_xml(self, client):
        res = await client.get("/sitemap.xml")
        assert res.status_code == 200
        assert "xml" in res.headers["content-type"]

    async def test_sitemap_has_all_urls(self, client):
        res = await client.get("/sitemap.xml")
        count = res.text.count("<loc>")
        assert count >= 168, f"sitemap has only {count} URLs"

    async def test_sitemap_urls_absolute(self, client):
        res = await client.get("/sitemap.xml")
        assert "<loc>https://mystral.space/" in res.text


class TestHealth:
    async def test_health(self, client):
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


class TestLangPages:
    """TZ-037c: subdirectory language versions. Tests run with GROQ_API_KEY=""
    so body content is the per-language fallback — chrome/metadata still come
    from seo_i18n static data and are fully assertable."""

    async def test_es_zodiac_sign(self, client):
        res = await client.get("/es/zodiac/scorpio")
        assert res.status_code == 200
        assert '<html lang="es">' in res.text
        assert '<link rel="canonical" href="https://mystral.space/es/zodiac/scorpio">' in res.text
        assert "Escorpio" in res.text

    async def test_es_zodiac_hreflang_full_set(self, client):
        res = await client.get("/es/zodiac/scorpio")
        for hl, url in [
            ("ru", "https://mystral.space/zodiac/scorpio"),
            ("en", "https://mystral.space/en/zodiac/scorpio"),
            ("es", "https://mystral.space/es/zodiac/scorpio"),
            ("pt", "https://mystral.space/pt/zodiac/scorpio"),
            ("tr", "https://mystral.space/tr/zodiac/scorpio"),
            ("uk", "https://mystral.space/uk/zodiac/scorpio"),
        ]:
            assert f'hreflang="{hl}" href="{url}"' in res.text, hl
        # x-default points at the Russian original
        assert 'hreflang="x-default" href="https://mystral.space/zodiac/scorpio"' in res.text

    async def test_tr_tarot_card(self, client):
        res = await client.get("/tr/tarot/the-fool")
        assert res.status_code == 200
        assert '<html lang="tr">' in res.text
        assert "Deli" in res.text  # Turkish name for The Fool

    async def test_uk_rune(self, client):
        res = await client.get("/uk/runes/fehu")
        assert res.status_code == 200
        assert '<html lang="uk">' in res.text
        assert "Феху" in res.text

    async def test_en_numerology(self, client):
        res = await client.get("/en/numerology/life-path-1")
        assert res.status_code == 200
        assert '<html lang="en">' in res.text
        assert "Life Path Number 1" in res.text

    async def test_es_natal_planet(self, client):
        res = await client.get("/es/natal-chart/planets/sun")
        assert res.status_code == 200
        assert '<html lang="es">' in res.text
        assert "Sol" in res.text  # Spanish name for the Sun

    async def test_pt_lunar_day(self, client):
        res = await client.get("/pt/lunar-calendar/day/1")
        assert res.status_code == 200
        assert '<html lang="pt">' in res.text
        assert "Dia das Intenções" in res.text  # Portuguese title for lunar day 1

    async def test_lang_hubs(self, client):
        for path in ("/es/zodiac", "/es/tarot", "/es/runes", "/es/natal-chart", "/es/lunar-calendar"):
            res = await client.get(path)
            assert res.status_code == 200, path
            assert '<html lang="es">' in res.text, path

    async def test_lang_constellation_svg(self, client):
        res = await client.get("/es/zodiac/scorpio/constellation.svg")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("image/svg")
        assert "ESCORPIO" in res.text  # localized sign name inside the SVG

    async def test_fallback_pages_are_noindex(self, client):
        # GROQ_API_KEY is empty in tests -> content is always the fallback,
        # which must never be indexable
        res = await client.get("/es/zodiac/scorpio")
        assert 'content="noindex, follow"' in res.text

    async def test_hub_pages_are_indexable(self, client):
        # hubs have no generated content, so no fallback -> index, follow
        res = await client.get("/es/zodiac")
        assert 'content="index, follow"' in res.text

    async def test_language_switcher_links(self, client):
        res = await client.get("/es/zodiac/scorpio")
        assert 'href="https://mystral.space/uk/zodiac/scorpio" hreflang="uk">Українська</a>' in res.text
        # current language is a non-link span
        assert "<span>Español</span>" in res.text


class TestLangValidation:
    async def test_unknown_lang_404(self, client):
        res = await client.get("/de/zodiac/scorpio")
        assert res.status_code == 404

    async def test_unknown_lang_hub_404(self, client):
        res = await client.get("/xx/zodiac")
        assert res.status_code == 404

    async def test_valid_lang_invalid_slug_404(self, client):
        res = await client.get("/es/zodiac/dragonborn")
        assert res.status_code == 404

    async def test_lang_traversal_slug_404(self, client):
        res = await client.get("/es/zodiac/..%2F..%2Fetc%2Fpasswd")
        assert res.status_code == 404


class TestLangRedirects:
    """Old hreflang markup advertised ?lang=xx URLs — they must 301 to the
    real subdirectory versions now."""

    async def test_legacy_query_lang_redirects(self, client):
        res = await client.get("/zodiac/scorpio?lang=es", follow_redirects=False)
        assert res.status_code == 301
        assert res.headers["location"] == "/es/zodiac/scorpio"

    async def test_legacy_query_lang_hub_redirects(self, client):
        res = await client.get("/tarot?lang=uk", follow_redirects=False)
        assert res.status_code == 301
        assert res.headers["location"] == "/uk/tarot"

    async def test_query_lang_ru_serves_page(self, client):
        res = await client.get("/zodiac/scorpio?lang=ru", follow_redirects=False)
        assert res.status_code == 200

    async def test_query_lang_garbage_serves_ru_page(self, client):
        res = await client.get("/zodiac/scorpio?lang=klingon", follow_redirects=False)
        assert res.status_code == 200
        assert '<html lang="ru">' in res.text


class TestRuRegression:
    """Russian pages keep their URLs, canonical and chrome exactly."""

    async def test_ru_canonical_stays_root(self, client):
        res = await client.get("/zodiac/scorpio")
        assert '<link rel="canonical" href="https://mystral.space/zodiac/scorpio">' in res.text
        assert '<html lang="ru">' in res.text

    async def test_ru_title_unchanged(self, client):
        res = await client.get("/zodiac/scorpio")
        assert "<title>Скорпион — характеристика, гороскоп и совместимость | Mystral</title>" in res.text

    async def test_ru_breadcrumbs_unchanged(self, client):
        res = await client.get("/zodiac/scorpio")
        assert 'Главная</a> › <a href="/zodiac">Знаки зодиака</a> › Скорпион' in res.text

    async def test_ru_hreflang_now_includes_en(self, client):
        res = await client.get("/zodiac/scorpio")
        assert 'hreflang="en" href="https://mystral.space/en/zodiac/scorpio"' in res.text
        # the old broken ?lang= alternates are gone
        assert "?lang=" not in res.text

    async def test_ru_pages_have_no_ru_prefix_links(self, client):
        res = await client.get("/zodiac/scorpio")
        assert "/ru/zodiac" not in res.text

    async def test_numerology_breadcrumb_jsonld_no_dead_hub(self, client):
        # the numerology hub does not exist; JSON-LD must not reference it
        res = await client.get("/numerology/life-path-1")
        assert res.status_code == 200
        assert '"item":"https://mystral.space/numerology"' not in res.text


class TestSitemapI18n:
    async def test_sitemap_contains_lang_urls(self, client):
        res = await client.get("/sitemap.xml")
        assert "<loc>https://mystral.space/es/zodiac/aries</loc>" in res.text
        assert "<loc>https://mystral.space/uk/tarot/the-fool</loc>" in res.text
        assert "<loc>https://mystral.space/en/numerology/life-path-1</loc>" in res.text
        assert "<loc>https://mystral.space/es/natal-chart/planets/sun</loc>" in res.text
        assert "<loc>https://mystral.space/uk/lunar-calendar/day/1</loc>" in res.text
        assert "<loc>https://mystral.space/natal-chart</loc>" in res.text
        assert "<loc>https://mystral.space/lunar-calendar</loc>" in res.text

    async def test_sitemap_has_xhtml_alternates(self, client):
        res = await client.get("/sitemap.xml")
        assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in res.text
        assert '<xhtml:link rel="alternate" hreflang="x-default"' in res.text

    async def test_sitemap_full_count(self, client):
        res = await client.get("/sitemap.xml")
        count = res.text.count("<loc>")
        # 1 homepage + 168 paths x 6 languages (126 original + 2 new hubs
        # + 10 natal planets + 30 lunar days, added in TZ-083)
        assert count == 1009, f"sitemap has {count} URLs"

    async def test_sitemap_is_wellformed_xml(self, client):
        import xml.etree.ElementTree as ET
        res = await client.get("/sitemap.xml")
        ET.fromstring(res.text)  # raises on malformed XML
