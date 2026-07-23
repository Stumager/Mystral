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

        with patch("app.api.v1.numerology.safe_groq_stream", side_effect=fast_stream):
            res = await client.post("/v1/numerology/interpret", headers=auth_headers, json={"section": "core", "lang": "ru"})
        assert res.status_code == 200

    async def test_a_full_request_releases_its_own_lock(self, client, auth_headers, auth_user):
        """The endpoint itself must release the lock once its stream ends,
        so a second, separate request right after succeeds."""
        user, _ = auth_user

        async def fast_stream(*a, **k):
            yield "data: [DONE]\n\n"

        with patch("app.api.v1.numerology.safe_groq_stream", side_effect=fast_stream):
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

        with patch("app.api.v1.numerology.safe_groq_stream", side_effect=fast_stream):
            other_user = await client.post("/v1/numerology/interpret", headers=pro_headers, json={"section": "core", "lang": "ru"})
        assert other_user.status_code == 200
