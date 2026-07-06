import re


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


class TestSitemap:
    async def test_sitemap_returns_xml(self, client):
        res = await client.get("/sitemap.xml")
        assert res.status_code == 200
        assert "xml" in res.headers["content-type"]

    async def test_sitemap_has_all_urls(self, client):
        res = await client.get("/sitemap.xml")
        count = res.text.count("<loc>")
        assert count >= 126, f"sitemap has only {count} URLs"

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

    async def test_lang_hubs(self, client):
        for path in ("/es/zodiac", "/es/tarot", "/es/runes"):
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

    async def test_sitemap_has_xhtml_alternates(self, client):
        res = await client.get("/sitemap.xml")
        assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in res.text
        assert '<xhtml:link rel="alternate" hreflang="x-default"' in res.text

    async def test_sitemap_full_count(self, client):
        res = await client.get("/sitemap.xml")
        count = res.text.count("<loc>")
        # 1 homepage + 126 paths x 6 languages
        assert count == 757, f"sitemap has {count} URLs"

    async def test_sitemap_is_wellformed_xml(self, client):
        import xml.etree.ElementTree as ET
        res = await client.get("/sitemap.xml")
        ET.fromstring(res.text)  # raises on malformed XML
