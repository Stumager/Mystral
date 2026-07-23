"""QA-035/036: /numerology/interpret already had an hourly quota
(check_rate_limit), but it never set an actual Retry-After header and had no
guard against a user firing several requests back-to-back within that quota —
each one reached the LLM and held a DB connection for its full stream
duration, so a burst could queue up and stall. check_rate_limit now attaches
Retry-After; check_not_in_flight/release_in_flight add a one-generation-per-
user-per-endpoint lock, tested directly here (endpoint-level behavior is
covered in test_numerology_security.py).
"""
import pytest
from fastapi import HTTPException

from app.core.limiter import check_not_in_flight, check_rate_limit, release_in_flight


class TestCheckRateLimitRetryAfter:
    async def test_over_limit_raises_429_with_retry_after_header(self):
        for _ in range(2):
            await check_rate_limit("u1", "free", "limiter_test", 2, 20)
        with pytest.raises(HTTPException) as exc:
            await check_rate_limit("u1", "free", "limiter_test", 2, 20)
        assert exc.value.status_code == 429
        assert "Retry-After" in exc.value.headers
        assert int(exc.value.headers["Retry-After"]) > 0
        assert exc.value.detail["retry_after"] == int(exc.value.headers["Retry-After"])


class TestInFlightGuard:
    async def test_second_call_blocked_while_first_not_released(self):
        await check_not_in_flight("u1", "numerology_interpret")
        with pytest.raises(HTTPException) as exc:
            await check_not_in_flight("u1", "numerology_interpret")
        assert exc.value.status_code == 429
        assert "Retry-After" in exc.value.headers

    async def test_allowed_again_after_release(self):
        await check_not_in_flight("u1", "numerology_interpret")
        await release_in_flight("u1", "numerology_interpret")
        await check_not_in_flight("u1", "numerology_interpret")

    async def test_lock_is_independent_per_user(self):
        await check_not_in_flight("u1", "numerology_interpret")
        await check_not_in_flight("u2", "numerology_interpret")

    async def test_lock_is_independent_per_endpoint(self):
        await check_not_in_flight("u1", "numerology_interpret")
        await check_not_in_flight("u1", "tarot_interpret")
