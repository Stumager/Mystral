"""Daily-horoscope push notification generation (app/services/horoscope.py).

A production push was observed cut off mid-sentence — the same
max_tokens-too-tight class of bug fixed for SEO generation in TZ-060.
"""
from unittest.mock import AsyncMock, patch

from app.services.horoscope import GENERATION_MAX_TOKENS, generate_horoscope


class TestHoroscopeGeneration:
    def test_max_tokens_has_real_headroom_over_the_value_that_truncated(self):
        # Regression guard: 200 caused a real production truncation
        # ("...day for" with nothing after it).
        assert GENERATION_MAX_TOKENS >= 500

    async def test_truncated_response_is_logged(self, caplog):
        import logging

        fake_message = type("M", (), {"content": "Сфера: финансы. Неблагоприятный день для"})()
        fake_choice = type("C", (), {"message": fake_message, "finish_reason": "length"})()
        fake_resp = type("R", (), {"choices": [fake_choice]})()

        fake_client = AsyncMock()
        fake_client.chat.completions.create = AsyncMock(return_value=fake_resp)

        with patch("app.services.horoscope._get_async_client", return_value=fake_client):
            with caplog.at_level(logging.WARNING, logger="app.services.horoscope"):
                text = await generate_horoscope("scorpio", "ru")

        assert text == "Сфера: финансы. Неблагоприятный день для"
        assert any("finish_reason=length" in r.message for r in caplog.records)

    async def test_complete_response_is_not_logged_as_truncated(self, caplog):
        import logging

        fake_message = type("M", (), {"content": "Полный текст гороскопа без обрывов."})()
        fake_choice = type("C", (), {"message": fake_message, "finish_reason": "stop"})()
        fake_resp = type("R", (), {"choices": [fake_choice]})()

        fake_client = AsyncMock()
        fake_client.chat.completions.create = AsyncMock(return_value=fake_resp)

        with patch("app.services.horoscope._get_async_client", return_value=fake_client):
            with caplog.at_level(logging.WARNING, logger="app.services.horoscope"):
                text = await generate_horoscope("leo", "en")

        assert text == "Полный текст гороскопа без обрывов."
        assert not any("finish_reason=length" in r.message for r in caplog.records)
