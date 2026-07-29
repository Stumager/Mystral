"""app/scheduler.py: daily horoscope push formatting.

A production push ("Гороскоп на сегодня") showed literal "**работа**" instead
of bold text. Root cause: messages are sent with parse_mode="HTML", which
doesn't understand Markdown at all — the LLM occasionally ignores the
prompt's no-Markdown instruction and emits **bold** anyway, which then shows
as literal asterisks. _sanitize_llm_text is the safety net on top of the
prompt-level fix (see app/services/horoscope.py).
"""
from datetime import date, datetime, timedelta
from unittest.mock import Mock

import httpx
import pytest

import app.api.v1.horoscope as horoscope_module
import app.scheduler as scheduler_module
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import AuthProvider, User, UserProfile
from app.scheduler import (
    _build_digest,
    _sanitize_llm_text,
    demote_expired_subscriptions,
    send_daily_horoscopes,
    send_subscription_reminders,
)
from tests.conftest import make_user

_REAL_POST = httpx.AsyncClient.post


def _tg_mock(calls: list):
    async def _fake(self, url, *args, **kwargs):
        if "api.telegram.org" in str(url):
            calls.append(kwargs.get("json") or {})
            resp = Mock()
            resp.status_code = 200
            resp.json = Mock(return_value={"ok": True})
            return resp
        return await _REAL_POST(self, url, *args, **kwargs)
    return _fake


class _FixedDatetime(datetime):
    """Freezes send_daily_horoscopes' now_utc at 09:02 on the REAL current
    date (not a hardcoded one) — so eligibility (local hour==9, minute<5)
    doesn't depend on when the suite happens to run, while still landing on
    whatever calendar day date.today() resolves to inside
    get_cached_or_generate_horoscope. Hardcoding an unrelated fixed date here
    would risk exactly the kind of date-basis mismatch TZ-104 is about."""

    @classmethod
    def now(cls, tz=None):
        today = date.today()
        return datetime(today.year, today.month, today.day, 9, 2, tzinfo=tz)


class _FixedDatetime857(datetime):
    """TZ-107: freezes now_utc at 08:57 — one tick (5 min) before the 9:00
    delivery window opens, the moment the pre-warm logic should fire for a
    UTC-timezone user."""

    @classmethod
    def now(cls, tz=None):
        today = date.today()
        return datetime(today.year, today.month, today.day, 8, 57, tzinfo=tz)


@pytest.fixture
def frozen_9am(monkeypatch):
    monkeypatch.setattr(scheduler_module, "datetime", _FixedDatetime)


@pytest.fixture
def frozen_857am(monkeypatch):
    monkeypatch.setattr(scheduler_module, "datetime", _FixedDatetime857)


async def _make_notif_user(tg_id: str = "999000", birth_date=date(1990, 8, 1),
                           lang: str = "ru", tz: str = "UTC") -> User:
    """A user eligible for send_daily_horoscopes: notifications on, timezone
    and birth_date set, Telegram auth provider. birth_date=Aug 1 -> Leo."""
    user, _ = await make_user(email=f"{tg_id}@test.com", with_profile=False)
    async with AsyncSessionLocal() as s:
        u = await s.get(User, user.id)
        u.lang = lang
        s.add(u)
        s.add(UserProfile(user_id=user.id, birth_date=birth_date,
                          timezone=tz, notifications_enabled=True))
        s.add(AuthProvider(user_id=user.id, provider="telegram", provider_id=tg_id))
        await s.commit()
    return user


async def _make_pro_user_with_telegram(expires_at, tg_id: str = "123456") -> User:
    user, _ = await make_user(email=f"{tg_id}@test.com", tier="pro", with_profile=False)
    async with AsyncSessionLocal() as s:
        u = await s.get(User, user.id)
        u.subscription_expires_at = expires_at
        s.add(u)
        s.add(AuthProvider(user_id=user.id, provider="telegram", provider_id=tg_id))
        await s.commit()
    return user


class TestSanitizeLlmText:
    def test_markdown_bold_converted_to_html(self):
        assert _sanitize_llm_text("Ключевая сфера — **работа**.") == \
            "Ключевая сфера — <b>работа</b>."

    def test_plain_text_untouched(self):
        text = "Совет: не начинайте новых проектов сегодня."
        assert _sanitize_llm_text(text) == text

    def test_html_metacharacters_escaped(self):
        # Unescaped `<`/`&` would otherwise risk breaking Telegram's HTML
        # parser entirely, not just rendering wrong.
        assert _sanitize_llm_text("Доход < расхода & это плохо") == \
            "Доход &lt; расхода &amp; это плохо"

    def test_multiple_bold_spans(self):
        assert _sanitize_llm_text("**Первое** и **второе**.") == \
            "<b>Первое</b> и <b>второе</b>."


class TestDemoteExpiredSubscriptions:
    """TZ-075: active sweep — the only prior mechanism was the lazy check in
    deps.get_current_user, which only ran on that user's own next request, so
    an inactive expired user stayed tier="pro" in the DB indefinitely."""

    async def test_expired_pro_user_is_demoted(self, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        user = await _make_pro_user_with_telegram(datetime.utcnow() - timedelta(hours=1))
        await demote_expired_subscriptions()

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"
            assert u.subscription_expires_at is None

        assert len(calls) == 1
        assert "истекла" in calls[0]["text"]

    async def test_active_pro_user_is_untouched(self, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        expiry = datetime.utcnow() + timedelta(days=1)
        user = await _make_pro_user_with_telegram(expiry)
        await demote_expired_subscriptions()

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "pro"
            assert u.subscription_expires_at == expiry

        assert calls == []

    async def test_demotion_happens_even_without_telegram_token(self):
        # settings.telegram_bot_token is "" by default in tests (conftest) —
        # demotion must not depend on notification delivery succeeding.
        user = await _make_pro_user_with_telegram(datetime.utcnow() - timedelta(hours=1))
        await demote_expired_subscriptions()

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"

    async def test_no_expired_users_is_a_noop(self):
        await demote_expired_subscriptions()  # must not raise with an empty table


class TestSendSubscriptionReminders:
    """TZ-075: the expiry-day branch moved to demote_expired_subscriptions
    (fires at the real cutoff instead of a date-only match) — this job now
    only sends the advance 3-day warning, which is genuinely date-based."""

    async def test_three_day_warning_still_sent(self, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        await _make_pro_user_with_telegram(datetime.utcnow() + timedelta(days=3))
        await send_subscription_reminders()

        assert len(calls) == 1
        assert "через 3 дня" in calls[0]["text"]

    async def test_no_longer_sends_expiry_notice_for_today(self, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        await _make_pro_user_with_telegram(datetime.utcnow())
        await send_subscription_reminders()

        assert calls == []


async def _fake_complete_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
    yield 'data: {"text": "Первое предложение дня. "}\n\n'
    yield 'data: {"text": "Второе предложение с советом. "}\n\n'
    yield 'data: {"text": "Третье предложение — итог."}\n\n'
    if on_finish:
        on_finish("stop")
    yield "data: [DONE]\n\n"


async def _fake_empty_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
    # Simulates a total generation failure (e.g. a network/API error inside
    # safe_groq_stream) — only the error/DONE frames, no "text" chunks at all.
    if on_finish:
        on_finish("stop")
    yield "data: [DONE]\n\n"


class TestBuildDigest:
    """Pure string trimming (app/scheduler.py), not a second AI call. TZ-104:
    replaces the push's own independent generation, whose prompt always
    enumerated life areas in the same fixed, never-randomized order
    ("работа" listed first every time) — see PROGRESS.md for the Step 0
    writeup of why that produced the "always работа" pattern."""

    def test_short_text_returned_unchanged(self):
        text = "Один день — одна возможность. Действуй уверенно."
        assert _build_digest(text) == text

    def test_empty_text_returns_empty(self):
        assert _build_digest("") == ""
        assert _build_digest("   ") == ""

    def test_long_text_is_trimmed_with_ellipsis(self):
        text = ("Предложение номер один. Предложение номер два. "
                "Предложение номер три. Предложение номер четыре. "
                "Предложение номер пять.")
        digest = _build_digest(text, max_chars=50)
        assert digest.endswith("…")
        assert digest != text
        assert len(digest) < len(text)

    def test_never_cuts_a_sentence_mid_word(self):
        text = "Раз. Два. Три четыре пять шесть семь восемь девять десять одиннадцать двенадцать."
        digest = _build_digest(text, max_chars=10)
        body = digest.rstrip("…")
        assert body.endswith(".")

    def test_first_sentence_alone_exceeding_budget_is_still_returned_whole(self):
        long_first = "X" * 60 + "."
        text = f"{long_first} Короткое второе предложение."
        digest = _build_digest(text, max_chars=20)
        assert digest.startswith(long_first)
        assert digest.endswith("…")

    def test_single_long_sentence_with_no_punctuation_is_returned_whole(self):
        # No sentence-ending punctuation anywhere -> nothing to safely trim
        # at, so the whole thing comes back rather than an empty/cut result.
        text = ("слово " * 40).strip()
        digest = _build_digest(text, max_chars=20)
        assert digest == text
        assert "…" not in digest

    def test_collapses_whitespace_and_newlines(self):
        text = "Первое.\n\n\nВторое.   Третье."
        assert _build_digest(text) == "Первое. Второе. Третье."

    def test_stops_at_the_configured_budget(self):
        text = "A" * 30 + ". " + "B" * 30 + ". " + "C" * 30 + "."
        digest = _build_digest(text, max_chars=40)
        assert len(digest) <= 41  # +1 for the appended ellipsis character


class TestSendDailyHoroscopesDigest:
    """TZ-104: the push must be a digest of the SAME cached horoscope the app
    shows for that sign+lang+day (not an independently generated text with
    its own, differently-biased prompt), and must never go out before that
    cache entry exists for the day."""

    async def test_cache_hit_is_used_verbatim_no_generation(self, monkeypatch, frozen_9am):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        def _explode(*a, **k):
            raise AssertionError("safe_groq_stream must not run on a cache hit")
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _explode)

        await _make_notif_user()
        today = date.today().isoformat()
        cache_key = f"horoscope:leo:ru:{today}"
        digest_key = f"horoscope_digest:leo:ru:{today}"
        cached_text = ("Сегодня Солнце подчёркивает вашу решительность. "
                       "Используйте утро для важных разговоров. Вечером — отдых.")
        await horoscope_module.redis_client.set(cache_key, cached_text, ex=86400)
        # TZ-107: the digest is now its own cached AI paraphrase (see
        # get_cached_or_generate_digest) — it must also be a cache hit here,
        # or the "no generation at all" guarantee this test checks wouldn't
        # actually hold.
        await horoscope_module.redis_client.set(digest_key, "Кэшированный пересказ дня.", ex=86400)

        await send_daily_horoscopes()

        assert len(calls) == 1
        assert "Кэшированный пересказ дня." in calls[0]["text"]

    async def test_cache_miss_generates_and_caches_before_sending(self, monkeypatch, frozen_9am):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _fake_complete_stream)

        await _make_notif_user()
        today = date.today().isoformat()
        cache_key = f"horoscope:leo:ru:{today}"
        assert not await horoscope_module.redis_client.get(cache_key)

        await send_daily_horoscopes()

        assert len(calls) == 1
        # The push went out — but by the time it did, the SAME cache entry
        # the app's /horoscope/stream reads must already be populated. This
        # is the "can't go out before generated+cached" guarantee, checked
        # mechanically (the cache actually holds the full text) rather than
        # just trusting call order.
        cached_after = await horoscope_module.redis_client.get(cache_key)
        assert cached_after is not None
        assert "Первое предложение дня." in cached_after.decode()
        assert "Первое предложение дня." in calls[0]["text"]

    async def test_generation_failure_skips_user_without_marking_sent(self, monkeypatch, frozen_9am):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _fake_empty_stream)

        user = await _make_notif_user()
        await send_daily_horoscopes()

        assert calls == []
        today_local = date.today().strftime("%Y-%m-%d")
        dedup_key = f"daily_notif:{user.id}:{today_local}"
        assert not await horoscope_module.redis_client.get(dedup_key), \
            "must not mark as sent when nothing was actually sent — a later tick should retry"

    async def test_digest_is_a_real_ai_paraphrase_not_the_full_text(self, monkeypatch, frozen_9am):
        """TZ-107: the full horoscope is cached (so that generation is not
        re-run), but the digest is NOT — so send_daily_horoscopes must call
        get_cached_or_generate_digest, which runs its own short AI paraphrase
        of the cached text rather than sending the raw long text verbatim."""
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        async def _digest_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
            yield 'data: {"text": "Сегодня благоприятный день для новых начинаний."}\n\n'
            if on_finish:
                on_finish("stop")
            yield "data: [DONE]\n\n"
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _digest_stream)

        await _make_notif_user()
        today = date.today().isoformat()
        cache_key = f"horoscope:leo:ru:{today}"
        digest_key = f"horoscope_digest:leo:ru:{today}"
        long_text = (
            "Энергетика дня благоволит новым начинаниям и смелым решениям. "
            "Марс в тригоне к Солнцу даёт дополнительную уверенность в делах. "
            "Практика — используйте первую половину дня для переговоров, вечером избегайте конфликтов. "
            "Итог — доверяйте собственной интуиции сегодня, она не подведёт."
        )
        await horoscope_module.redis_client.set(cache_key, long_text, ex=86400)

        await send_daily_horoscopes()

        assert len(calls) == 1
        sent_text = calls[0]["text"]
        assert "Сегодня благоприятный день для новых начинаний." in sent_text
        assert long_text not in sent_text
        cached_digest = await horoscope_module.redis_client.get(digest_key)
        assert cached_digest.decode() == "Сегодня благоприятный день для новых начинаний."

    async def test_digest_generation_failure_falls_back_to_truncation(self, monkeypatch, frozen_9am):
        """If the digest-specific AI call fails or gets skip-cached for
        truncation, delivery must not be blocked entirely — the horoscope
        already generated fine, so it falls back to _build_digest's pure
        string trimming rather than skipping the user."""
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))

        async def _truncated_digest_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
            yield 'data: {"text": "Обрубленный пере"}\n\n'
            if on_finish:
                on_finish("length")
            yield "data: [DONE]\n\n"
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _truncated_digest_stream)

        await _make_notif_user()
        today = date.today().isoformat()
        cache_key = f"horoscope:leo:ru:{today}"
        digest_key = f"horoscope_digest:leo:ru:{today}"
        long_text = "Первое предложение. Второе предложение. Третье предложение."
        await horoscope_module.redis_client.set(cache_key, long_text, ex=86400)

        await send_daily_horoscopes()

        assert len(calls) == 1, "a digest hiccup must not stop delivery of an already-generated horoscope"
        expected_fallback = _build_digest(long_text)
        assert expected_fallback in calls[0]["text"]
        assert not await horoscope_module.redis_client.get(digest_key), \
            "the truncated digest must not be cached — the next call should retry generation"

    async def test_two_signs_same_day_get_independent_cache_entries(self, monkeypatch, frozen_9am):
        """Guards the cache-key format itself: TZ-104 must key on sign+lang,
        the exact same dimensions /horoscope/stream keys on, or two users
        with different signs would wrongly share (or clobber) one entry."""
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _fake_complete_stream)

        await _make_notif_user(tg_id="111222", birth_date=date(1990, 8, 1))  # Leo
        await _make_notif_user(tg_id="333444", birth_date=date(1990, 4, 1))  # Aries

        await send_daily_horoscopes()

        assert len(calls) == 2
        today = date.today().isoformat()
        assert await horoscope_module.redis_client.get(f"horoscope:leo:ru:{today}")
        assert await horoscope_module.redis_client.get(f"horoscope:aries:ru:{today}")

    async def test_prewarm_generates_one_tick_before_delivery_without_sending(self, monkeypatch, frozen_857am):
        """TZ-107: at 08:57 (one 5-min tick before this UTC user's 9:00
        window), the horoscope+digest for their sign+lang should already be
        generated and cached — but nothing should be sent yet, since their
        actual delivery window hasn't opened."""
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        calls: list = []
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock(calls))
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _fake_complete_stream)

        await _make_notif_user()
        today = date.today().isoformat()

        await send_daily_horoscopes()

        assert calls == [], "pre-warm must not send a message — the user's local 9:00 hasn't arrived yet"
        cached_horoscope = await horoscope_module.redis_client.get(f"horoscope:leo:ru:{today}")
        assert cached_horoscope is not None, "the full horoscope should be pre-generated a tick ahead of need"
        cached_digest = await horoscope_module.redis_client.get(f"horoscope_digest:leo:ru:{today}")
        assert cached_digest is not None, "the digest should also be pre-generated a tick ahead of need"

    async def test_prewarm_does_not_set_dedup_key(self, monkeypatch, frozen_857am):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        monkeypatch.setattr(httpx.AsyncClient, "post", _tg_mock([]))
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _fake_complete_stream)

        user = await _make_notif_user()
        await send_daily_horoscopes()

        today_local = date.today().strftime("%Y-%m-%d")
        dedup_key = f"daily_notif:{user.id}:{today_local}"
        assert not await horoscope_module.redis_client.get(dedup_key), \
            "pre-warm must not mark the user as notified — the real delivery tick still needs to send"

    async def test_generate_horoscope_no_longer_exists(self):
        """Regression guard: the biased independent-generation function this
        ticket retires must not quietly come back."""
        import app.services.horoscope as services_horoscope
        assert not hasattr(services_horoscope, "generate_horoscope")
        assert not hasattr(services_horoscope, "GENERATION_MAX_TOKENS")
