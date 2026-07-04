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
