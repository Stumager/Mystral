"""TZ-107: broadcast/app content desync investigation + digest AI-paraphrase
upgrade.

Step 0 found a real race condition: get_cached_or_generate_horoscope and
/horoscope/stream both did check-cache -> (on miss) generate -> write-cache
with no lock between the check and the write. Two callers landing in that
gap for the same sign+lang+day (e.g. the scheduler's push and a live app
request arriving at the same moment) each ran their own independent LLM
completion and could each show a *different* result before either write
landed — the confirmed mechanism behind a report of the broadcast showing
"Sun-Venus" while the app showed "Sun-Mars" for the same sign on the same
day. This file tests the NX-lock fix directly (TestConcurrentGenerationLock)
and the new AI-paraphrase digest that replaced pure string-truncation as the
push's primary teaser source (TestGetCachedOrGenerateDigest).
"""
import asyncio
from datetime import date

import app.api.v1.horoscope as horoscope_module


async def _complete_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
    yield 'data: {"text": "Короткий пересказ дня."}\n\n'
    if on_finish:
        on_finish("stop")
    yield "data: [DONE]\n\n"


async def _truncated_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
    yield 'data: {"text": "Обрубленный пере"}\n\n'
    if on_finish:
        on_finish("length")
    yield "data: [DONE]\n\n"


async def _empty_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
    if on_finish:
        on_finish("stop")
    yield "data: [DONE]\n\n"


class TestConcurrentGenerationLock:
    async def test_concurrent_cache_miss_only_generates_once(self, monkeypatch):
        call_count = 0

        async def _one_slow_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.2)
            yield 'data: {"text": "Единственная генерация."}\n\n'
            if on_finish:
                on_finish("stop")
            yield "data: [DONE]\n\n"

        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _one_slow_stream)

        results = await asyncio.gather(
            horoscope_module.get_cached_or_generate_horoscope("leo", "ru"),
            horoscope_module.get_cached_or_generate_horoscope("leo", "ru"),
        )

        assert call_count == 1, (
            "the second concurrent caller must wait for the first's result "
            "instead of also calling the LLM — this is the exact mechanism "
            "that let the broadcast and the app show different content for "
            "the same sign+lang+day"
        )
        assert results[0] == results[1] == "Единственная генерация."

    async def test_lock_is_released_after_generation_completes(self, monkeypatch):
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _complete_stream)
        today = date.today().isoformat()
        cache_key = f"horoscope:aries:ru:{today}"

        text = await horoscope_module.get_cached_or_generate_horoscope("aries", "ru")

        assert text == "Короткий пересказ дня."
        assert not await horoscope_module.redis_client.exists(f"lock:{cache_key}"), \
            "the lock must be released once generation completes, not held for its full TTL"

    async def test_concurrent_callers_for_different_signs_both_generate(self, monkeypatch):
        # The lock is keyed on the full cache key (sign+lang+day) — two
        # different signs must not block each other.
        call_count = 0

        async def _counting_stream(messages, max_tokens=1400, lang="ru", on_finish=None):
            nonlocal call_count
            call_count += 1
            yield 'data: {"text": "Текст."}\n\n'
            if on_finish:
                on_finish("stop")
            yield "data: [DONE]\n\n"

        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _counting_stream)

        await asyncio.gather(
            horoscope_module.get_cached_or_generate_horoscope("taurus", "ru"),
            horoscope_module.get_cached_or_generate_horoscope("gemini", "ru"),
        )

        assert call_count == 2


class TestGetCachedOrGenerateDigest:
    async def test_returns_cached_digest_without_generating(self, monkeypatch):
        def _explode(*a, **k):
            raise AssertionError("must not generate on a digest cache hit")
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _explode)

        today = date.today().isoformat()
        await horoscope_module.redis_client.set(f"horoscope:leo:ru:{today}", "Полный текст.", ex=86400)
        await horoscope_module.redis_client.set(f"horoscope_digest:leo:ru:{today}", "Кэшированный пересказ.", ex=86400)

        result = await horoscope_module.get_cached_or_generate_digest("leo", "ru")
        assert result == "Кэшированный пересказ."

    async def test_generates_real_paraphrase_and_caches_on_miss(self, monkeypatch):
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _complete_stream)
        today = date.today().isoformat()
        full_key = f"horoscope:leo:ru:{today}"
        digest_key = f"horoscope_digest:leo:ru:{today}"
        long_text = "Полный длинный текст гороскопа на сегодня с подробностями."
        await horoscope_module.redis_client.set(full_key, long_text, ex=86400)

        result = await horoscope_module.get_cached_or_generate_digest("leo", "ru")

        assert result == "Короткий пересказ дня."
        assert result != long_text, "this must be a real AI paraphrase, not the raw cached horoscope text"
        cached = await horoscope_module.redis_client.get(digest_key)
        assert cached.decode() == "Короткий пересказ дня."

    async def test_truncated_digest_is_not_cached_and_returns_empty(self, monkeypatch):
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _truncated_stream)
        today = date.today().isoformat()
        await horoscope_module.redis_client.set(f"horoscope:leo:ru:{today}", "Полный текст гороскопа.", ex=86400)

        result = await horoscope_module.get_cached_or_generate_digest("leo", "ru")

        assert result == "", "a truncated digest must be reported as unavailable, not returned cut off"
        assert not await horoscope_module.redis_client.get(f"horoscope_digest:leo:ru:{today}"), \
            "must not cache a truncated result — the next call should retry generation"

    async def test_generation_failure_returns_empty(self, monkeypatch):
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _empty_stream)
        today = date.today().isoformat()
        await horoscope_module.redis_client.set(f"horoscope:leo:ru:{today}", "Полный текст гороскопа.", ex=86400)

        result = await horoscope_module.get_cached_or_generate_digest("leo", "ru")
        assert result == ""

    async def test_returns_empty_when_full_horoscope_unavailable(self, monkeypatch):
        async def _empty_horoscope(sign, lang):
            return ""
        monkeypatch.setattr(horoscope_module, "get_cached_or_generate_horoscope", _empty_horoscope)

        def _explode(*a, **k):
            raise AssertionError("must not attempt a digest without a full horoscope to paraphrase")
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _explode)

        result = await horoscope_module.get_cached_or_generate_digest("virgo", "ru")
        assert result == ""

    async def test_uses_digest_specific_max_tokens(self, monkeypatch):
        captured = {}

        async def _capture(messages, max_tokens=1400, lang="ru", on_finish=None):
            captured["max_tokens"] = max_tokens
            yield 'data: {"text": "Пересказ."}\n\n'
            if on_finish:
                on_finish("stop")
            yield "data: [DONE]\n\n"

        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _capture)
        today = date.today().isoformat()
        await horoscope_module.redis_client.set(f"horoscope:leo:ru:{today}", "Полный текст гороскопа.", ex=86400)

        await horoscope_module.get_cached_or_generate_digest("leo", "ru")

        assert captured["max_tokens"] == horoscope_module.DIGEST_GENERATION_MAX_TOKENS
        assert captured["max_tokens"] != horoscope_module.GENERATION_MAX_TOKENS

    async def test_different_langs_cache_independently(self, monkeypatch):
        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _complete_stream)
        today = date.today().isoformat()
        await horoscope_module.redis_client.set(f"horoscope:leo:ru:{today}", "RU текст.", ex=86400)
        await horoscope_module.redis_client.set(f"horoscope:leo:en:{today}", "EN text.", ex=86400)

        await horoscope_module.get_cached_or_generate_digest("leo", "ru")
        await horoscope_module.get_cached_or_generate_digest("leo", "en")

        assert await horoscope_module.redis_client.get(f"horoscope_digest:leo:ru:{today}")
        assert await horoscope_module.redis_client.get(f"horoscope_digest:leo:en:{today}")


class TestStreamEndpointConcurrentLock:
    """The endpoint-level counterpart to TestConcurrentGenerationLock: two
    concurrent /horoscope/stream requests for the same sign+lang+day (e.g.
    the scheduler's pre-warm racing a live app viewer, the exact scenario
    behind the reported content desync) must not each run their own
    generation — the second must wait and stream back the first's result."""

    async def test_two_concurrent_requests_only_generate_once(self, client, auth_headers, monkeypatch):
        call_count = 0

        async def _one_slow_stream(*a, **k):
            nonlocal call_count
            call_count += 1
            on_finish = k.get("on_finish")
            await asyncio.sleep(0.2)
            yield 'data: {"text": "Единственный текст."}\n\n'
            if on_finish:
                on_finish("stop")
            yield "data: [DONE]\n\n"

        monkeypatch.setattr(horoscope_module, "safe_groq_stream", _one_slow_stream)

        first, second = await asyncio.gather(
            client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "cancer", "lang": "ru"}),
            client.post("/v1/horoscope/stream", headers=auth_headers, json={"sign": "cancer", "lang": "ru"}),
        )

        def _extract(body: str) -> str:
            out = ""
            for line in body.split("\n"):
                if not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                try:
                    out += __import__("json").loads(data).get("text", "")
                except Exception:
                    pass
            return out

        assert call_count == 1, (
            "the second request must wait for the first's generation instead "
            "of also calling the LLM — otherwise two viewers of the same "
            "sign+lang+day can see genuinely different generated content"
        )
        assert _extract(first.text) == "Единственный текст."
        assert _extract(second.text) == "Единственный текст."
