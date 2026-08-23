"""TZ-120: app/core/cached_stream.py — the shared helper that made Matrix's
(karmic tail/money line/base points/children/compatibility), Numerology's
core/square/karmic sections, and Compatibility's per-type/composite
interpretations stop re-billing the LLM for a repeat view of already-seen,
fully deterministic content.

Unit-level tests against cached_groq_stream() directly, decoupled from any
one endpoint — the endpoint-level integration (does a real second HTTP call
actually skip the mock) is covered per-module in test_matrix.py,
test_karmic_tail.py, etc. via their existing "prompt" test classes calling
the same cache key twice.
"""
import json
from unittest.mock import patch

import pytest

from app.core.cached_stream import (
    cached_groq_stream,
    interpretation_cache_key,
    name_fingerprint,
    peek_cached_interpretation,
)


async def _fake_llm_stream(messages, max_tokens=900, lang="ru", on_finish=None):
    yield 'data: {"text": "Hello "}\n\n'
    yield 'data: {"text": "world"}\n\n'
    if on_finish:
        on_finish("stop")
    yield "data: [DONE]\n\n"


async def _fake_llm_stream_truncated(messages, max_tokens=900, lang="ru", on_finish=None):
    yield 'data: {"text": "Cut off"}\n\n'
    if on_finish:
        on_finish("length")
    yield "data: [DONE]\n\n"


async def _fake_llm_stream_error(messages, max_tokens=900, lang="ru", on_finish=None):
    yield 'data: {"error": "timeout", "message": "AI service not responding"}\n\n'


async def _drain(gen):
    return [line async for line in gen]


class TestInterpretationCacheKey:
    def test_deterministic_for_same_inputs(self):
        assert interpretation_cache_key("matrix", "1990-05-15", "core", "ru") == \
            interpretation_cache_key("matrix", "1990-05-15", "core", "ru")

    def test_differs_when_any_part_differs(self):
        base = interpretation_cache_key("matrix", "1990-05-15", "core", "ru")
        assert interpretation_cache_key("matrix", "1990-05-16", "core", "ru") != base
        assert interpretation_cache_key("matrix", "1990-05-15", "talents", "ru") != base
        assert interpretation_cache_key("matrix", "1990-05-15", "core", "en") != base
        assert interpretation_cache_key("karmic_tail", "1990-05-15", "core", "ru") != base


class TestNameFingerprint:
    def test_stable_for_same_name(self):
        assert name_fingerprint("Alex") == name_fingerprint("Alex")

    def test_case_and_whitespace_insensitive(self):
        assert name_fingerprint("Alex") == name_fingerprint(" alex ")

    def test_differs_for_different_names(self):
        assert name_fingerprint("Alex") != name_fingerprint("Sasha")

    def test_none_and_empty_are_a_stable_sentinel(self):
        assert name_fingerprint(None) == name_fingerprint("")
        assert name_fingerprint(None) == "none"


class TestCachedGroqStreamMiss:
    async def test_first_call_streams_live_and_caches(self):
        key = interpretation_cache_key("test", "miss-1")
        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream):
            lines = await _drain(cached_groq_stream(key, [], lang="ru"))
        text = "".join(json.loads(l[6:])["text"] for l in lines if l.startswith("data: ") and "text" in l)
        assert text == "Hello world"

        cached = await peek_cached_interpretation(key)
        assert cached == "Hello world"

    async def test_second_call_serves_from_cache_without_hitting_the_llm(self):
        key = interpretation_cache_key("test", "miss-2")
        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream):
            await _drain(cached_groq_stream(key, [], lang="ru"))

        with patch("app.core.cached_stream.safe_groq_stream") as mock_llm:
            lines = await _drain(cached_groq_stream(key, [], lang="ru"))
            mock_llm.assert_not_called()
        text = "".join(json.loads(l[6:])["text"] for l in lines if l.startswith("data: ") and "text" in l)
        assert text == "Hello world"

    async def test_cached_response_still_ends_with_done(self):
        key = interpretation_cache_key("test", "done-marker")
        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream):
            await _drain(cached_groq_stream(key, [], lang="ru"))
        lines = await _drain(cached_groq_stream(key, [], lang="ru"))
        assert lines[-1] == "data: [DONE]\n\n"


class TestCachedGroqStreamDoesNotCacheFailures:
    async def test_truncated_generation_is_not_cached(self):
        """finish_reason == "length" means max_tokens cut the reply short —
        caching that would permanently serve an incomplete reading."""
        key = interpretation_cache_key("test", "truncated")
        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream_truncated):
            await _drain(cached_groq_stream(key, [], lang="ru"))
        assert await peek_cached_interpretation(key) is None

    async def test_error_event_is_not_cached(self):
        key = interpretation_cache_key("test", "errored")
        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream_error):
            lines = await _drain(cached_groq_stream(key, [], lang="ru"))
        assert any("error" in l for l in lines)
        assert await peek_cached_interpretation(key) is None

    async def test_a_later_call_after_a_failure_retries_live(self):
        key = interpretation_cache_key("test", "retry-after-fail")
        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream_error):
            await _drain(cached_groq_stream(key, [], lang="ru"))

        with patch("app.core.cached_stream.safe_groq_stream", _fake_llm_stream) as mock_llm:
            lines = await _drain(cached_groq_stream(key, [], lang="ru"))
        text = "".join(json.loads(l[6:])["text"] for l in lines if l.startswith("data: ") and "text" in l)
        assert text == "Hello world"


class TestPeekCachedInterpretation:
    async def test_none_when_nothing_cached(self):
        key = interpretation_cache_key("test", "never-populated")
        assert await peek_cached_interpretation(key) is None

    async def test_redis_read_failure_falls_back_to_none_not_an_exception(self):
        key = interpretation_cache_key("test", "redis-down")
        with patch("app.core.cached_stream._redis") as mock_redis:
            mock_redis.get.side_effect = Exception("connection refused")
            assert await peek_cached_interpretation(key) is None
