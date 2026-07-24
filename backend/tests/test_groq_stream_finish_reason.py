"""Follow-up to QA-015/016 (horoscopes cutting off mid-sentence for
ES/PT/TR): safe_groq_stream's streaming path never surfaced finish_reason,
unlike the two non-streaming AI generation paths (seo_generator,
services/horoscope) which already learned to detect and log
finish_reason == "length" truncation. on_finish lets a caller react to a
truncated generation (e.g. skip caching it) without changing the SSE
yield contract that every other caller of safe_groq_stream depends on.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.core.groq_client import safe_groq_stream


def _chunk(text: str | None, finish_reason: str | None = None):
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text), finish_reason=finish_reason)])


class _FakeStream:
    def __init__(self, chunks):
        self._chunks = chunks

    def __aiter__(self):
        return self._iter()

    async def _iter(self):
        for c in self._chunks:
            yield c


def _fake_client(chunks):
    client = SimpleNamespace()
    client.chat = SimpleNamespace()
    client.chat.completions = SimpleNamespace()
    client.chat.completions.create = AsyncMock(return_value=_FakeStream(chunks))
    return client


class TestSafeGroqStreamFinishReason:
    async def test_on_finish_receives_stop_for_a_complete_generation(self):
        chunks = [_chunk("Hello "), _chunk("world"), _chunk(None, finish_reason="stop")]
        seen = []
        with patch("app.core.groq_client._get_async_client", return_value=_fake_client(chunks)):
            async for _ in safe_groq_stream([{"role": "system", "content": "x"}], lang="en", on_finish=seen.append):
                pass
        assert seen == ["stop"]

    async def test_on_finish_receives_length_when_truncated(self):
        chunks = [_chunk("Cut off mid"), _chunk(None, finish_reason="length")]
        seen = []
        with patch("app.core.groq_client._get_async_client", return_value=_fake_client(chunks)):
            async for _ in safe_groq_stream([{"role": "system", "content": "x"}], lang="es", on_finish=seen.append):
                pass
        assert seen == ["length"]

    async def test_on_finish_is_optional_and_does_not_break_existing_callers(self):
        chunks = [_chunk("Hi"), _chunk(None, finish_reason="stop")]
        with patch("app.core.groq_client._get_async_client", return_value=_fake_client(chunks)):
            out = [c async for c in safe_groq_stream([{"role": "system", "content": "x"}], lang="en")]
        assert any('"text": "Hi"' in c for c in out)
        assert out[-1] == "data: [DONE]\n\n"

    async def test_truncation_is_logged(self, caplog):
        chunks = [_chunk("Cut off"), _chunk(None, finish_reason="length")]
        with patch("app.core.groq_client._get_async_client", return_value=_fake_client(chunks)):
            with caplog.at_level("WARNING"):
                async for _ in safe_groq_stream([{"role": "system", "content": "x"}], lang="tr"):
                    pass
        assert any("truncated" in r.message for r in caplog.records)
