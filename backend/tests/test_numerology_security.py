"""QA-035/036: burst load against /numerology/interpret degraded badly
(13.88s -> 48.42s across 6 back-to-back requests, 6th never responded) because
each request held its DB session open for the entire SSE stream and nothing
stopped a user from starting several generations at once. Fixed by releasing
the session right after the profile lookup and by capping each user to one
in-flight generation per endpoint (app/core/limiter.py's check_not_in_flight).

The in-flight guard is exercised here by pre-seeding the Redis lock directly
(check_not_in_flight) rather than racing two real concurrent requests through
the test ASGI transport, which serializes them and deadlocks (the second
request never starts until the first's stream — gated on a manually released
asyncio.Event — completes, and nothing ever sets that event).
"""
from unittest.mock import patch

from app.core.limiter import check_not_in_flight, release_in_flight


class TestNumerologyInterpretInFlightGuard:
    async def test_blocked_while_lock_held(self, client, auth_headers, auth_user):
        user, _ = auth_user
        await check_not_in_flight(str(user.id), "numerology_interpret")

        res = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
        assert res.status_code == 429
        # retry_after in the JSON body only here — the raw HTTP Retry-After
        # header is asserted separately once main.py's exception-handler
        # header-forwarding fix lands (that bug drops headers on every
        # HTTPException app-wide, not just this one).
        assert res.json()["retry_after"] > 0

    async def test_allowed_after_lock_released(self, client, auth_headers, auth_user):
        user, _ = auth_user
        await check_not_in_flight(str(user.id), "numerology_interpret")
        await release_in_flight(str(user.id), "numerology_interpret")

        async def fast_stream(*a, **k):
            yield "data: [DONE]\n\n"

        with patch("app.core.cached_stream.safe_groq_stream", side_effect=fast_stream):
            res = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
        assert res.status_code == 200

    async def test_a_full_request_releases_its_own_lock(self, client, auth_headers, auth_user):
        """The endpoint itself must release the lock once its stream ends,
        so a second, separate request right after succeeds."""
        user, _ = auth_user

        async def fast_stream(*a, **k):
            yield "data: [DONE]\n\n"

        with patch("app.core.cached_stream.safe_groq_stream", side_effect=fast_stream):
            first = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
            assert first.status_code == 200
            second = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
        assert second.status_code == 200

    async def test_lock_is_per_user(self, client, auth_headers, pro_headers, auth_user):
        user, _ = auth_user
        await check_not_in_flight(str(user.id), "numerology_interpret")

        blocked = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
        assert blocked.status_code == 429

        async def fast_stream(*a, **k):
            yield "data: [DONE]\n\n"

        with patch("app.core.cached_stream.safe_groq_stream", side_effect=fast_stream):
            other_user = await client.post("/v1/numerology/interpret", headers=pro_headers, json={"section": "core", "lang": "ru"})
        assert other_user.status_code == 200


class TestRetryAfterHeaderReachesClient:
    """TZ-091: main.py's StarletteHTTPException handler rebuilt the response
    from exc.detail alone and dropped exc.headers along the way, so the
    Retry-After set by check_not_in_flight (and check_rate_limit) never
    actually reached the client — app-wide, not just here. TestNumerology-
    InterpretInFlightGuard.test_blocked_while_lock_held above only checks
    the JSON body's retry_after field for exactly that reason; this asserts
    the raw HTTP header specifically, now that the handler forwards it."""

    async def test_in_flight_429_carries_retry_after_header(self, client, auth_headers, auth_user):
        user, _ = auth_user
        await check_not_in_flight(str(user.id), "numerology_interpret")

        res = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
        assert res.status_code == 429
        assert "Retry-After" in res.headers
        assert int(res.headers["Retry-After"]) == res.json()["retry_after"]


def _fake_stream_completed(messages, max_tokens=900, lang="ru", on_finish=None):
    async def _gen():
        yield 'data: {"text": "reading"}\n\n'
        if on_finish:
            on_finish("stop")
        yield "data: [DONE]\n\n"
    return _gen()


class TestNumerologyInterpretCaching:
    """TZ-120: core/square/karmic are pure functions of birth_date (+ name
    for core) — cached. "forecast" depends on today's date (personal year/
    month/day) and must NEVER be cached, or a user would get stuck reading
    yesterday's forecast forever."""

    async def test_core_section_second_request_does_not_call_the_llm(self, client, auth_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream_completed):
            first = await client.post("/v1/numerology/interpret", headers=auth_headers,
                                      json={"section": "core", "lang": "ru"})
        assert first.status_code == 200

        with patch("app.core.cached_stream.safe_groq_stream") as mock_llm:
            second = await client.post("/v1/numerology/interpret", headers=auth_headers,
                                       json={"section": "core", "lang": "ru"})
            mock_llm.assert_not_called()
        assert second.status_code == 200

    async def test_square_section_is_also_cached(self, client, auth_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream_completed):
            await client.post("/v1/numerology/interpret", headers=auth_headers,
                              json={"section": "square", "lang": "ru"})
        with patch("app.core.cached_stream.safe_groq_stream") as mock_llm:
            await client.post("/v1/numerology/interpret", headers=auth_headers,
                              json={"section": "square", "lang": "ru"})
            mock_llm.assert_not_called()

    async def test_karmic_section_is_also_cached(self, client, auth_headers):
        with patch("app.core.cached_stream.safe_groq_stream", _fake_stream_completed):
            await client.post("/v1/numerology/interpret", headers=auth_headers,
                              json={"section": "karmic", "lang": "ru"})
        with patch("app.core.cached_stream.safe_groq_stream") as mock_llm:
            await client.post("/v1/numerology/interpret", headers=auth_headers,
                              json={"section": "karmic", "lang": "ru"})
            mock_llm.assert_not_called()

    async def test_forecast_section_is_never_cached(self, client, pro_headers):
        """The one deliberate exception — personal year/month/day change
        over time, so every request must reach the live model, proven by
        counting actual invocations of the (plain, non-Mock) fake stream.
        forecast isn't the free "core" exception, hence pro_headers here.
        Patches app.api.v1.numerology.safe_groq_stream specifically — the
        forecast branch never goes through cached_stream at all (cache_key
        stays None), so that's the real call site for this one path."""
        calls = {"n": 0}

        def _counting_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            calls["n"] += 1
            return _fake_stream_completed(messages, max_tokens, lang, on_finish)

        with patch("app.api.v1.numerology.safe_groq_stream", _counting_stream):
            r1 = await client.post("/v1/numerology/interpret", headers=pro_headers,
                                   json={"section": "forecast", "lang": "ru"})
            r2 = await client.post("/v1/numerology/interpret", headers=pro_headers,
                                   json={"section": "forecast", "lang": "ru"})
        assert r1.status_code == 200 and r2.status_code == 200
        assert calls["n"] == 2
