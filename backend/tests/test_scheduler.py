"""app/scheduler.py: daily horoscope push formatting.

A production push ("Гороскоп на сегодня") showed literal "**работа**" instead
of bold text. Root cause: messages are sent with parse_mode="HTML", which
doesn't understand Markdown at all — the LLM occasionally ignores the
prompt's no-Markdown instruction and emits **bold** anyway, which then shows
as literal asterisks. _sanitize_llm_text is the safety net on top of the
prompt-level fix (see app/services/horoscope.py).
"""
from app.scheduler import _sanitize_llm_text


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
