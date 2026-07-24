"""Live-observed follow-up to QA-015/016: ES/PT/TR daily horoscopes were
cutting off mid-sentence in the web app. Root cause: /horoscope/stream had
no finish_reason check (unlike the offline/non-streaming AI paths, which
already learned this lesson) and a max_tokens ceiling of 700 — tight for a
"three paragraphs, 150-250 words" prompt. Worse, a truncated result used to
get cached in Redis for 24h exactly like a complete one, serving the same
broken cut-off text to every subsequent viewer of that sign/lang/day.
"""
import json
from unittest.mock import patch

import app.api.v1.horoscope as horoscope_module


def _extract_sse_text(body: str) -> str:
    out = ""
    for line in body.split("\n"):
        if not line.startswith("data: "):
            continue
        data = line[6:].strip()
        if data == "[DONE]":
            break
        try:
            out += json.loads(data).get("text", "")
        except Exception:
            pass
    return out


async def _complete_stream(*a, **k):
    on_finish = k.get("on_finish")
    yield 'data: {"text": "Full "}\n\n'
    yield 'data: {"text": "text."}\n\n'
    if on_finish:
        on_finish("stop")
    yield "data: [DONE]\n\n"


async def _truncated_stream(*a, **k):
    on_finish = k.get("on_finish")
    yield 'data: {"text": "Cut off mid"}\n\n'
    if on_finish:
        on_finish("length")
    yield "data: [DONE]\n\n"


class TestHoroscopeTruncationHandling:
    async def test_complete_generation_is_cached(self, client, auth_headers):
        with patch("app.api.v1.horoscope.safe_groq_stream", side_effect=_complete_stream) as mock_stream:
            first = await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "aries", "lang": "es"})
            second = await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "aries", "lang": "es"})

        assert _extract_sse_text(first.text) == "Full text."
        assert _extract_sse_text(second.text) == "Full text."
        assert mock_stream.call_count == 1, "second request should be served from cache"

    async def test_truncated_generation_is_not_cached(self, client, auth_headers):
        with patch("app.api.v1.horoscope.safe_groq_stream", side_effect=_truncated_stream) as mock_stream:
            first = await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "aries", "lang": "es"})
            second = await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "aries", "lang": "es"})

        assert _extract_sse_text(first.text) == "Cut off mid"
        assert _extract_sse_text(second.text) == "Cut off mid"
        assert mock_stream.call_count == 2, "a truncated result must not be cached — every request should retry"

    async def test_stream_call_uses_raised_token_ceiling(self, client, auth_headers):
        with patch("app.api.v1.horoscope.safe_groq_stream", side_effect=_complete_stream) as mock_stream:
            await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "aries", "lang": "pt"})

        _, kwargs = mock_stream.call_args
        assert kwargs["max_tokens"] == horoscope_module.GENERATION_MAX_TOKENS
        assert horoscope_module.GENERATION_MAX_TOKENS > 700, "the old 700 ceiling was too tight for a 150-250 word prompt"

    async def test_different_languages_cache_independently(self, client, auth_headers):
        with patch("app.api.v1.horoscope.safe_groq_stream", side_effect=_complete_stream) as mock_stream:
            await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "leo", "lang": "es"})
            await client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "leo", "lang": "ru"})

        assert mock_stream.call_count == 2, "each language must get its own generation, not share the RU cache entry"
