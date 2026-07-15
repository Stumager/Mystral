"""app/scheduler.py: daily horoscope push formatting.

A production push ("Гороскоп на сегодня") showed literal "**работа**" instead
of bold text. Root cause: messages are sent with parse_mode="HTML", which
doesn't understand Markdown at all — the LLM occasionally ignores the
prompt's no-Markdown instruction and emits **bold** anyway, which then shows
as literal asterisks. _sanitize_llm_text is the safety net on top of the
prompt-level fix (see app/services/horoscope.py).
"""
from datetime import datetime, timedelta
from unittest.mock import Mock

import httpx

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import AuthProvider, User
from app.scheduler import _sanitize_llm_text, demote_expired_subscriptions, send_subscription_reminders
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
