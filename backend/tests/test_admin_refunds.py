from datetime import datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import httpx
from sqlmodel import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import AuthProvider, Payment, RefundRequest, User
from tests.conftest import make_user

# Same technique as test_payments.py: the test client is itself an httpx.AsyncClient
# (ASGITransport-based), so a blanket patch of AsyncClient.post would intercept our
# OWN test requests too. These wrappers only fake calls to the real provider domain
# and fall through to the genuine method for everything else.
_REAL_POST = httpx.AsyncClient.post


def _provider_post_mock(domain: str, json_data: dict, status_code: int = 200):
    async def _fake(self, url, *args, **kwargs):
        if domain in str(url):
            resp = Mock()
            resp.status_code = status_code
            resp.json = Mock(return_value=json_data)
            return resp
        return await _REAL_POST(self, url, *args, **kwargs)
    return _fake


class TestAdminRefundsAuth:
    async def test_list_requires_admin_token(self, client):
        res = await client.get("/v1/admin/refunds")
        assert res.status_code == 403

    async def test_approve_requires_admin_token(self, client):
        res = await client.post(f"/v1/admin/refunds/{uuid4()}/approve")
        assert res.status_code == 403

    async def test_reject_requires_admin_token(self, client):
        res = await client.post(f"/v1/admin/refunds/{uuid4()}/reject", json={"comment": "no"})
        assert res.status_code == 403


class TestAdminRefundsModeration:
    async def _make_pending_request(self, provider="yukassa", tg_id=None, product="pro_month", amount="399.00"):
        user, headers = await make_user(email=f"modtest-{uuid4()}@test.com", tier="pro")
        async with AsyncSessionLocal() as s:
            if tg_id:
                s.add(AuthProvider(user_id=user.id, provider="telegram", provider_id=tg_id))
            payment = Payment(
                user_id=user.id, provider=provider,
                provider_payment_id=f"{provider}-charge-{uuid4()}",
                product=product, amount=amount,
                currency="XTR" if provider == "stars" else "RUB",
                status="succeeded",
            )
            s.add(payment)
            await s.commit()
            await s.refresh(payment)

            refund_req = RefundRequest(user_id=user.id, payment_id=payment.id, reason="testing")
            s.add(refund_req)
            await s.commit()
            await s.refresh(refund_req)
        return user, headers, payment, refund_req

    async def test_list_shows_pending(self, client, admin_headers):
        _, _, payment, refund_req = await self._make_pending_request()
        res = await client.get("/v1/admin/refunds", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        ids = [r["id"] for r in data["pending"]]
        assert str(refund_req.id) in ids
        assert data["resolved"] == [] or all(r["id"] != str(refund_req.id) for r in data["resolved"])

    async def test_approve_unknown_request(self, client, admin_headers):
        res = await client.post(f"/v1/admin/refunds/{uuid4()}/approve", headers=admin_headers)
        assert res.status_code == 404

    async def test_approve_yukassa_completes(self, client, admin_headers, monkeypatch):
        _, _, payment, refund_req = await self._make_pending_request(provider="yukassa")
        monkeypatch.setattr(httpx.AsyncClient, "post",
                             _provider_post_mock("api.yookassa.ru", {"id": "re-1", "status": "succeeded"}, 200))

        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "completed"

        async with AsyncSessionLocal() as s:
            req = await s.get(RefundRequest, refund_req.id)
            assert req.status == "completed"
            assert req.resolved_at is not None
            # approve does NOT touch Pro/payment.status itself — that's the
            # webhook's job once YuKassa confirms the refund for real
            pay = await s.get(Payment, payment.id)
            assert pay.status == "succeeded"

    async def test_approve_stars_completes(self, client, admin_headers, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        _, _, payment, refund_req = await self._make_pending_request(provider="stars", tg_id="555111")
        monkeypatch.setattr(httpx.AsyncClient, "post",
                             _provider_post_mock("api.telegram.org", {"ok": True, "result": True}, 200))

        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "completed"

        async with AsyncSessionLocal() as s:
            req = await s.get(RefundRequest, refund_req.id)
            assert req.status == "completed"

    async def test_approve_stars_without_telegram_account_fails(self, client, admin_headers, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "test-bot-token")
        _, _, payment, refund_req = await self._make_pending_request(provider="stars", tg_id=None)

        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "failed"

        async with AsyncSessionLocal() as s:
            req = await s.get(RefundRequest, refund_req.id)
            assert req.status == "failed"
            assert "Telegram account" in req.error_detail

    async def test_approve_provider_error_marks_failed_not_500(self, client, admin_headers, monkeypatch):
        """A provider rejection (e.g. YuKassa says already refunded) must
        surface as a clean failed status, never a 500."""
        _, _, payment, refund_req = await self._make_pending_request(provider="yukassa")
        monkeypatch.setattr(httpx.AsyncClient, "post",
                             _provider_post_mock("api.yookassa.ru", {"description": "already refunded"}, 400))

        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "failed"
        assert data["error"] == "already refunded"

        async with AsyncSessionLocal() as s:
            req = await s.get(RefundRequest, refund_req.id)
            assert req.status == "failed"
            assert req.error_detail == "already refunded"

    async def test_approve_already_refunded_payment_short_circuits(self, client, admin_headers, monkeypatch):
        """If the payment was already refunded outside this system (e.g. by
        hand in the YuKassa dashboard), approving must not call the provider
        again — just fail cleanly."""
        _, _, payment, refund_req = await self._make_pending_request(provider="yukassa")
        async with AsyncSessionLocal() as s:
            pay = await s.get(Payment, payment.id)
            pay.status = "refunded"
            s.add(pay)
            await s.commit()

        called = {"n": 0}

        async def _fail_if_called(self, url, *a, **k):
            if "api.yookassa.ru" in str(url):
                called["n"] += 1
                raise AssertionError("provider should not be called")
            return await _REAL_POST(self, url, *a, **k)

        monkeypatch.setattr(httpx.AsyncClient, "post", _fail_if_called)

        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "failed"
        assert called["n"] == 0

    async def test_approve_twice_is_protected(self, client, admin_headers, monkeypatch):
        _, _, payment, refund_req = await self._make_pending_request(provider="yukassa")
        monkeypatch.setattr(httpx.AsyncClient, "post",
                             _provider_post_mock("api.yookassa.ru", {"id": "re-2", "status": "succeeded"}, 200))

        first = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert first.status_code == 200
        second = await client.post(f"/v1/admin/refunds/{refund_req.id}/approve", headers=admin_headers)
        assert second.status_code == 400

    async def test_reject_requires_comment(self, client, admin_headers):
        _, _, payment, refund_req = await self._make_pending_request()
        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/reject",
                                headers=admin_headers, json={"comment": ""})
        assert res.status_code == 422

    async def test_reject_success(self, client, admin_headers):
        _, _, payment, refund_req = await self._make_pending_request()
        res = await client.post(f"/v1/admin/refunds/{refund_req.id}/reject",
                                headers=admin_headers, json={"comment": "Not eligible"})
        assert res.status_code == 200
        assert res.json()["status"] == "rejected"

        async with AsyncSessionLocal() as s:
            req = await s.get(RefundRequest, refund_req.id)
            assert req.status == "rejected"
            assert req.admin_comment == "Not eligible"
            u = await s.get(User, req.user_id)
            assert u.subscription_tier == "pro"  # rejection never touches Pro

    async def test_reject_already_resolved_is_protected(self, client, admin_headers):
        _, _, payment, refund_req = await self._make_pending_request()
        first = await client.post(f"/v1/admin/refunds/{refund_req.id}/reject",
                                  headers=admin_headers, json={"comment": "no"})
        assert first.status_code == 200
        second = await client.post(f"/v1/admin/refunds/{refund_req.id}/reject",
                                   headers=admin_headers, json={"comment": "no again"})
        assert second.status_code == 400


class TestDeleteUserCascade:
    """Found via live verification against real Postgres: delete_user's manual
    cascade list predates Payment (TZ-038b/055) and never included it, so
    deleting a user with any payment history violated the payments_user_id_fkey
    constraint. SQLite in tests doesn't enforce FKs by default, so this was
    invisible here until RefundRequest (TZ-065) made it concrete. Both tables
    are now in the cascade list — this guards against it regressing."""

    async def test_delete_user_with_payment_and_refund_request(self, client, admin_headers):
        user, _ = await make_user(email=f"cascade-{uuid4()}@test.com")
        async with AsyncSessionLocal() as s:
            payment = Payment(user_id=user.id, provider="yukassa",
                              provider_payment_id=f"cascade-{uuid4()}",
                              product="pro_month", amount="399.00", status="succeeded")
            s.add(payment)
            await s.commit()
            await s.refresh(payment)
            s.add(RefundRequest(user_id=user.id, payment_id=payment.id, reason="cascade test"))
            await s.commit()

        res = await client.delete(f"/v1/admin/users/{user.id}", headers=admin_headers)
        assert res.status_code == 200

        async with AsyncSessionLocal() as s:
            assert await s.get(User, user.id) is None
            assert (await s.exec(select(Payment).where(Payment.user_id == user.id))).first() is None
            assert (await s.exec(select(RefundRequest).where(RefundRequest.user_id == user.id))).first() is None


class TestAdminSubscriptionStatusIsRecomputed:
    """TZ-075: subscription_tier is only ever flipped to "free" lazily on that
    user's own next authenticated request (deps.py) or by the hourly
    demote_expired_subscriptions sweep — an inactive expired user can sit at
    tier="pro" in the DB indefinitely otherwise. The admin endpoints must not
    surface that stale raw value."""

    async def _make_stale_pro_user(self, expires_at, email: str) -> User:
        user, _ = await make_user(email=email, tier="pro", with_profile=False)
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            u.subscription_expires_at = expires_at
            s.add(u)
            await s.commit()
        return user

    async def test_expired_user_shows_free_in_users_list(self, client, admin_headers):
        user = await self._make_stale_pro_user(
            datetime.utcnow() - timedelta(hours=1), "stale-expired@test.com")

        res = await client.get("/v1/admin/users?search=stale-expired", headers=admin_headers)
        assert res.status_code == 200
        rows = res.json()["users"]
        assert len(rows) == 1
        assert rows[0]["tier"] == "free"

        # display-only recompute — the DB row itself is untouched (that stays
        # the job's/lazy check's responsibility, not this read endpoint's)
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "pro"

    async def test_active_user_still_shows_pro_in_users_list(self, client, admin_headers):
        await self._make_stale_pro_user(
            datetime.utcnow() + timedelta(days=1), "stale-active@test.com")

        res = await client.get("/v1/admin/users?search=stale-active", headers=admin_headers)
        rows = res.json()["users"]
        assert len(rows) == 1
        assert rows[0]["tier"] == "pro"

    async def test_expired_user_excluded_from_pro_stats_count(self, client, admin_headers):
        before = (await client.get("/v1/admin/stats", headers=admin_headers)).json()["pro_users"]
        await self._make_stale_pro_user(
            datetime.utcnow() - timedelta(hours=1), "stale-stats@test.com")

        after = (await client.get("/v1/admin/stats", headers=admin_headers)).json()["pro_users"]
        assert after == before
