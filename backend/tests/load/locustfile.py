"""Load scenarios for mystral.space.

Run:
    locust -f locustfile.py --headless -u 50 -r 5 --run-time 60s --host https://mystral.space

Scenario weights follow the QA plan: 70% returning user, 20% content reader, 10% SEO bot.

NOTE (intentional deviations from the original plan, see QA_AUDIT_REPORT.md):
- The register flow is NOT exercised against production: it creates junk accounts,
  sends real Resend emails and trips the 5/hour/IP rate limit by design.
  Set LOAD_TEST_REGISTER=1 only against a staging environment.
- Authenticated flows require real credentials: set LOAD_TEST_EMAIL / LOAD_TEST_PASSWORD.
  Without them the "returning user" runs the public (unauthenticated) surface,
  which is what an anonymous visitor and the SEO crawler hit anyway.
"""
import os
import random

from locust import HttpUser, between, constant, task

ZODIAC_SLUGS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
                "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
TAROT_SLUGS = ["the-fool", "the-magician", "the-empress", "the-tower", "the-sun"]
RUNE_SLUGS = ["fehu", "uruz", "ansuz", "raido", "algiz"]

TEST_EMAIL = os.getenv("LOAD_TEST_EMAIL", "")
TEST_PASSWORD = os.getenv("LOAD_TEST_PASSWORD", "")
ENABLE_REGISTER = os.getenv("LOAD_TEST_REGISTER", "") == "1"


class ReturningUser(HttpUser):
    """70% — a user opening the app: home data, horoscope, lunar day."""
    weight = 7
    wait_time = between(5, 30)
    token: str | None = None

    def on_start(self):
        if TEST_EMAIL and TEST_PASSWORD:
            res = self.client.post("/api/v1/auth/login",
                                   json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                                   name="/auth/login")
            if res.status_code == 200:
                self.token = res.json().get("access_token")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    def home(self):
        self.client.get("/", name="/")

    @task(3)
    def lunar_today(self):
        self.client.get("/api/v1/lunar/today?lang=ru", name="/lunar/today")

    @task(2)
    def horoscope_scores(self):
        sign = random.choice(ZODIAC_SLUGS)
        self.client.get(f"/api/v1/horoscope/scores?sign={sign}", name="/horoscope/scores")

    @task(1)
    def profile(self):
        if self.token:
            self.client.get("/api/v1/profile", headers=self._headers(), name="/profile")

    @task(1)
    def horoscope_stream(self):
        if self.token:
            with self.client.post("/api/v1/horoscope/stream",
                                  json={"sign": random.choice(ZODIAC_SLUGS), "lang": "ru"},
                                  headers=self._headers(), stream=True,
                                  name="/horoscope/stream", catch_response=True) as res:
                if res.status_code == 200:
                    for _ in res.iter_lines():
                        pass
                    res.success()
                else:
                    res.failure(f"HTTP {res.status_code}")


class ContentReader(HttpUser):
    """20% — anonymous visitor browsing SEO content."""
    weight = 2
    wait_time = between(3, 15)

    @task(3)
    def zodiac_page(self):
        self.client.get(f"/zodiac/{random.choice(ZODIAC_SLUGS)}", name="/zodiac/[slug]")

    @task(2)
    def tarot_page(self):
        self.client.get(f"/tarot/{random.choice(TAROT_SLUGS)}", name="/tarot/[slug]")

    @task(1)
    def rune_page(self):
        self.client.get(f"/runes/{random.choice(RUNE_SLUGS)}", name="/runes/[slug]")


class SeoBot(HttpUser):
    """10% — crawler: no think time."""
    weight = 1
    wait_time = constant(0)

    @task(2)
    def crawl_pages(self):
        self.client.get(f"/zodiac/{random.choice(ZODIAC_SLUGS)}", name="bot /zodiac/[slug]")
        self.client.get(f"/tarot/{random.choice(TAROT_SLUGS)}", name="bot /tarot/[slug]")
        self.client.get(f"/runes/{random.choice(RUNE_SLUGS)}", name="bot /runes/[slug]")

    @task(1)
    def sitemap(self):
        self.client.get("/sitemap.xml", name="bot /sitemap.xml")


if ENABLE_REGISTER:
    class NewUser(HttpUser):
        """Staging only: register + verify flow (trips prod rate limits by design)."""
        weight = 2
        wait_time = between(2, 8)

        @task
        def register(self):
            n = random.randint(100000, 999999)
            self.client.post("/api/v1/auth/register",
                             json={"email": f"load{n}@example.com",
                                   "password": "LoadTest1",
                                   "name": f"Load {n}"},
                             name="/auth/register")
