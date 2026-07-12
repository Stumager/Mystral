from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

import httpx
from sqlmodel import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import Payment, User
from tests.conftest import make_user

# The test client (conftest's `client` fixture) is itself an httpx.AsyncClient
# (ASGITransport-based), so a blanket patch of AsyncClient.post/.get would
# intercept our OWN test requests too. These wrappers only fake calls whose
# URL targets YuKassa's real domain and fall through to the genuine method
# (captured before patching) for everything else — i.e. the app's own ASGI calls.
_REAL_POST = httpx.AsyncClient.post
_REAL_GET = httpx.AsyncClient.get


def _yk_response(status_code=200, json_data=None):
    resp = Mock()
    resp.status_code = status_code
    resp.json = Mock(return_value=json_data or {})
    return resp


def _yk_post_mock(json_data, status_code=200):
    async def _fake(self, url, *args, **kwargs):
        if "api.yookassa.ru" in str(url):
            return _yk_response(status_code, json_data)
        return await _REAL_POST(self, url, *args, **kwargs)
    return _fake


def _yk_get_mock(json_data, status_code=200):
    async def _fake(self, url, *args, **kwargs):
        if "api.yookassa.ru" in str(url):
            return _yk_response(status_code, json_data)
        return await _REAL_GET(self, url, *args, **kwargs)
    return _fake


class TestStarsFlow:
    async def test_stars_invoice_requires_config(self, client, auth_headers):
        """Without TELEGRAM_BOT_TOKEN the endpoint must fail closed, not crash."""
        res = await client.post("/v1/payments/stars/create",
                                headers=auth_headers, json={"product": "pro_month"})
        assert res.status_code == 503

    async def test_stars_invoice_unknown_product(self, client, auth_headers):
        res = await client.post("/v1/payments/stars/create",
                                headers=auth_headers, json={"product": "pro_forever"})
        assert res.status_code == 422

    async def test_stars_activate_requires_internal_token(self, client, auth_user):
        user, _ = auth_user
        res = await client.post("/v1/payments/stars/activate",
                                json={"payload": f"pro_month_{user.id}"})
        assert res.status_code == 403

    async def test_stars_successful_payment(self, client, auth_user, internal_headers):
        """Bot activates via internal token → user becomes Pro, marker set for confirm."""
        user, headers = auth_user
        payload = f"pro_year_{user.id}"
        res = await client.post("/v1/payments/stars/activate",
                                headers=internal_headers, json={"payload": payload})
        assert res.status_code == 200

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "pro"
            # pro_year must grant ~365 days, not fall back to 30
            assert (u.subscription_expires_at - datetime.utcnow()).days >= 360

        confirm = await client.post("/v1/payments/stars/confirm",
                                    headers=headers, json={"payload": payload})
        assert confirm.status_code == 200
        assert confirm.json()["status"] == "ok"

    async def test_stars_confirm_without_payment_pending(self, client, auth_user):
        """Client-only 'paid' event must NOT activate Pro (spoofable)."""
        user, headers = auth_user
        res = await client.post("/v1/payments/stars/confirm",
                                headers=headers, json={"payload": f"pro_year_{user.id}"})
        assert res.status_code == 200
        assert res.json()["status"] == "pending"
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"

    async def test_stars_confirm_foreign_payload_rejected(self, client, auth_user, pro_user):
        _, headers = auth_user
        other, _ = pro_user
        res = await client.post("/v1/payments/stars/confirm",
                                headers=headers, json={"payload": f"pro_month_{other.id}"})
        assert res.status_code == 403

    async def test_stars_activate_invalid_payload(self, client, internal_headers):
        res = await client.post("/v1/payments/stars/activate",
                                headers=internal_headers, json={"payload": "hack_payload"})
        assert res.status_code == 400

    async def test_stars_activate_persists_payment_row(self, client, auth_user, internal_headers):
        """TZ-064 prerequisite: without a recorded Payment row, a later refund
        event has nothing to look up. Activate must write one, like YuKassa's
        /create does for its own flow."""
        user, _ = auth_user
        payload = f"pro_month_{user.id}"
        res = await client.post("/v1/payments/stars/activate", headers=internal_headers,
                                json={"payload": payload, "telegram_payment_charge_id": "tg-charge-1"})
        assert res.status_code == 200

        async with AsyncSessionLocal() as s:
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "tg-charge-1"))
            payment = result.first()
            assert payment is not None
            assert payment.provider == "stars"
            assert payment.status == "succeeded"
            assert payment.user_id == user.id

    async def test_stars_activate_without_charge_id_does_not_crash(self, client, internal_headers, auth_user):
        """Missing charge id (e.g. an older bot build) must degrade gracefully —
        Pro still activates, just nothing recorded for a future refund lookup."""
        user, _ = auth_user
        res = await client.post("/v1/payments/stars/activate", headers=internal_headers,
                                json={"payload": f"pro_month_{user.id}"})
        assert res.status_code == 200


class TestRefund:
    async def _make_pro(self, created_hours_ago: float):
        user, headers = await make_user(email=f"ref{created_hours_ago}@test.com", tier="pro")
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            u.subscription_created_at = datetime.utcnow() - timedelta(hours=created_hours_ago)
            u.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
            s.add(u)
            await s.commit()
        return user, headers

    async def test_refund_request_within_24h(self, client):
        _, headers = await self._make_pro(1)
        res = await client.post("/v1/payments/refund-request",
                                headers=headers, json={"reason": "test"})
        assert res.status_code == 200
        assert res.json()["status"] == "sent"

    async def test_refund_request_after_24h(self, client):
        _, headers = await self._make_pro(30)
        res = await client.post("/v1/payments/refund-request",
                                headers=headers, json={"reason": "test"})
        assert res.status_code == 200
        assert res.json()["status"] == "expired"

    async def test_refund_request_duplicate(self, client):
        _, headers = await self._make_pro(2)
        first = await client.post("/v1/payments/refund-request",
                                  headers=headers, json={"reason": "one"})
        assert first.json()["status"] == "sent"
        second = await client.post("/v1/payments/refund-request",
                                   headers=headers, json={"reason": "two"})
        assert second.status_code == 400

    async def test_refund_request_free_user(self, client, auth_headers):
        res = await client.post("/v1/payments/refund-request",
                                headers=auth_headers, json={"reason": "x"})
        assert res.status_code == 400


class TestAdminGrant:
    async def test_grant_pro_admin_only(self, client, auth_user):
        user, _ = auth_user
        res = await client.post(f"/v1/admin/users/{user.id}/grant-pro", json={"days": 30})
        assert res.status_code == 403

    async def test_grant_pro_with_token(self, client, auth_user, admin_headers):
        user, _ = auth_user
        res = await client.post(f"/v1/admin/users/{user.id}/grant-pro",
                                headers=admin_headers, json={"days": 30})
        assert res.status_code == 200
        async with AsyncSessionLocal() as s:
            assert (await s.get(User, user.id)).subscription_tier == "pro"

    async def test_revoke_pro_admin_only(self, client, pro_user):
        user, _ = pro_user
        res = await client.post(f"/v1/admin/users/{user.id}/revoke-pro")
        assert res.status_code == 403

    async def test_revoke_pro_with_token(self, client, pro_user, admin_headers):
        user, _ = pro_user
        res = await client.post(f"/v1/admin/users/{user.id}/revoke-pro", headers=admin_headers)
        assert res.status_code == 200
        async with AsyncSessionLocal() as s:
            assert (await s.get(User, user.id)).subscription_tier == "free"


class TestYukassaFlow:
    async def _make_pending_payment(self, user_id, provider_payment_id="yk-test-1", product="pro_month"):
        async with AsyncSessionLocal() as s:
            payment = Payment(user_id=user_id, provider_payment_id=provider_payment_id,
                              product=product, amount="399.00")
            s.add(payment)
            await s.commit()
            await s.refresh(payment)
            return payment

    async def test_yukassa_create_requires_config(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr(settings, "yukassa_shop_id", "")
        res = await client.post("/v1/payments/yukassa/create",
                                headers=auth_headers, json={"product": "pro_month"})
        assert res.status_code == 503

    async def test_yukassa_create_unknown_product(self, client, auth_headers):
        res = await client.post("/v1/payments/yukassa/create",
                                headers=auth_headers, json={"product": "pro_forever"})
        assert res.status_code == 422

    async def test_yukassa_create_persists_payment_row(self, client, auth_user):
        user, headers = auth_user
        with patch("httpx.AsyncClient.post", _yk_post_mock({
            "id": "yk-create-1",
            "status": "pending",
            "confirmation": {"confirmation_url": "https://yookassa.ru/checkout/test"},
        })):
            res = await client.post("/v1/payments/yukassa/create",
                                    headers=headers, json={"product": "pro_month"})
        assert res.status_code == 200
        data = res.json()
        assert data["payment_url"] == "https://yookassa.ru/checkout/test"
        assert "payment_id" in data

        async with AsyncSessionLocal() as s:
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "yk-create-1"))
            payment = result.first()
            assert payment is not None
            assert payment.status == "pending"
            assert payment.user_id == user.id
            assert str(payment.id) == data["payment_id"]

    async def test_yukassa_webhook_succeeded_activates_pro(self, client, auth_user):
        user, _ = auth_user
        await self._make_pending_payment(user.id, "yk-succ-1", "pro_year")
        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "yk-succ-1", "status": "succeeded",
            "metadata": {"user_id": str(user.id), "product": "pro_year"},
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "payment.succeeded", "object": {"id": "yk-succ-1"}})
        assert res.status_code == 200
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "pro"
            assert (u.subscription_expires_at - datetime.utcnow()).days >= 360
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "yk-succ-1"))
            assert result.first().status == "succeeded"

    async def test_yukassa_webhook_canceled_updates_row_no_pro(self, client, auth_user):
        user, _ = auth_user
        await self._make_pending_payment(user.id, "yk-cancel-1")
        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "yk-cancel-1", "status": "canceled",
            "metadata": {"user_id": str(user.id), "product": "pro_month"},
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "payment.canceled", "object": {"id": "yk-cancel-1"}})
        assert res.status_code == 200
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "yk-cancel-1"))
            assert result.first().status == "canceled"

    async def test_yukassa_webhook_ignores_other_events(self, client):
        res = await client.post("/v1/payments/yukassa/webhook",
                                json={"event": "payment.waiting_for_capture", "object": {"id": "whatever"}})
        assert res.status_code == 200
        assert res.json()["status"] == "ignored"

    async def test_yukassa_webhook_no_double_activation_on_retry(self, client, auth_user):
        """Repeated webhook delivery for an already-succeeded payment must not
        push subscription_expires_at forward again — a real money-adjacent bug
        (free extra days on every YuKassa retry) if the idempotency guard broke."""
        user, _ = auth_user
        await self._make_pending_payment(user.id, "yk-retry-1", "pro_month")
        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "yk-retry-1", "status": "succeeded",
            "metadata": {"user_id": str(user.id), "product": "pro_month"},
        })):
            res1 = await client.post("/v1/payments/yukassa/webhook",
                                     json={"event": "payment.succeeded", "object": {"id": "yk-retry-1"}})
            assert res1.status_code == 200
            async with AsyncSessionLocal() as s:
                first_expiry = (await s.get(User, user.id)).subscription_expires_at

            res2 = await client.post("/v1/payments/yukassa/webhook",
                                     json={"event": "payment.succeeded", "object": {"id": "yk-retry-1"}})
            assert res2.status_code == 200
            async with AsyncSessionLocal() as s:
                assert (await s.get(User, user.id)).subscription_expires_at == first_expiry

    async def test_yukassa_status_requires_auth(self, client):
        res = await client.get(f"/v1/payments/yukassa/status/{uuid4()}")
        assert res.status_code == 401

    async def test_yukassa_status_404_unknown_id(self, client, auth_headers):
        res = await client.get(f"/v1/payments/yukassa/status/{uuid4()}", headers=auth_headers)
        assert res.status_code == 404

    async def test_yukassa_status_forbidden_for_other_user(self, client, auth_user, pro_user):
        user, _ = auth_user
        _, other_headers = pro_user
        payment = await self._make_pending_payment(user.id, "yk-forbidden-1")
        res = await client.get(f"/v1/payments/yukassa/status/{payment.id}", headers=other_headers)
        assert res.status_code == 403

    async def test_yukassa_status_pending_triggers_live_reverify(self, client, auth_user):
        user, headers = auth_user
        payment = await self._make_pending_payment(user.id, "yk-live-1", "pro_month")
        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "yk-live-1", "status": "succeeded",
            "metadata": {"user_id": str(user.id), "product": "pro_month"},
        })):
            res = await client.get(f"/v1/payments/yukassa/status/{payment.id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "succeeded"
        assert data["tier"] == "pro"


class TestYukassaRefund:
    """TZ-061: refund.succeeded must revoke Pro — a real production gap where
    a refunded payment left Pro active indefinitely."""

    async def _pay_and_activate(self, client, user, provider_payment_id, product="pro_month"):
        """Realistic setup: create the pending Payment row (as /yukassa/create
        would) and drive the actual payment.succeeded webhook (like
        TestYukassaFlow does) so the test starts from a genuine Pro-active +
        Payment(status="succeeded") state, not a hand-crafted one."""
        async with AsyncSessionLocal() as s:
            payment = Payment(user_id=user.id, provider_payment_id=provider_payment_id,
                              product=product, amount="399.00")
            s.add(payment)
            await s.commit()

        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": provider_payment_id, "status": "succeeded",
            "metadata": {"user_id": str(user.id), "product": product},
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "payment.succeeded", "object": {"id": provider_payment_id}})
        assert res.status_code == 200

    async def test_refund_webhook_revokes_pro(self, client, auth_user):
        user, _ = auth_user
        await self._pay_and_activate(client, user, "yk-refund-1")

        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "re-1", "status": "succeeded", "payment_id": "yk-refund-1",
            "amount": {"value": "399.00", "currency": "RUB"},
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "refund.succeeded", "object": {"id": "re-1"}})
        assert res.status_code == 200

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"
            assert u.subscription_expires_at is None
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "yk-refund-1"))
            assert result.first().status == "refunded"

    async def test_refund_webhook_partial_amount_still_revokes(self, client, auth_user):
        """Product decision: any refund amount revokes Pro, no comparison
        against the original payment amount."""
        user, _ = auth_user
        await self._pay_and_activate(client, user, "yk-refund-partial-1", "pro_year")

        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "re-partial-1", "status": "succeeded", "payment_id": "yk-refund-partial-1",
            "amount": {"value": "1.00", "currency": "RUB"},  # far less than the 2999.00 payment
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "refund.succeeded", "object": {"id": "re-partial-1"}})
        assert res.status_code == 200

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"

    async def test_refund_webhook_idempotent_on_retry(self, client, auth_user):
        user, _ = auth_user
        await self._pay_and_activate(client, user, "yk-refund-retry-1")

        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "re-retry-1", "status": "succeeded", "payment_id": "yk-refund-retry-1",
            "amount": {"value": "399.00", "currency": "RUB"},
        })):
            res1 = await client.post("/v1/payments/yukassa/webhook",
                                     json={"event": "refund.succeeded", "object": {"id": "re-retry-1"}})
            assert res1.status_code == 200
            res2 = await client.post("/v1/payments/yukassa/webhook",
                                     json={"event": "refund.succeeded", "object": {"id": "re-retry-1"}})
            assert res2.status_code == 200

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"
            assert u.subscription_expires_at is None
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "yk-refund-retry-1"))
            assert result.first().status == "refunded"

    async def test_refund_webhook_unknown_local_payment(self, client):
        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "re-unknown-1", "status": "succeeded", "payment_id": "yk-does-not-exist",
            "amount": {"value": "399.00", "currency": "RUB"},
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "refund.succeeded", "object": {"id": "re-unknown-1"}})
        assert res.status_code == 400

    async def test_refund_webhook_status_not_succeeded_ignored(self, client, auth_user):
        """Never trust the webhook body alone (TZ-055 discipline): if the
        re-fetched refund isn't actually "succeeded", Pro must not be revoked."""
        user, _ = auth_user
        await self._pay_and_activate(client, user, "yk-refund-pending-1")

        with patch("httpx.AsyncClient.get", _yk_get_mock({
            "id": "re-pending-1", "status": "pending", "payment_id": "yk-refund-pending-1",
            "amount": {"value": "399.00", "currency": "RUB"},
        })):
            res = await client.post("/v1/payments/yukassa/webhook",
                                    json={"event": "refund.succeeded", "object": {"id": "re-pending-1"}})
        assert res.status_code == 400

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "pro"

    async def test_refund_webhook_no_refund_id_ignored(self, client):
        res = await client.post("/v1/payments/yukassa/webhook",
                                json={"event": "refund.succeeded", "object": {}})
        assert res.status_code == 200
        assert res.json()["status"] == "no_refund_id"


class TestStarsRefund:
    """TZ-064: Telegram Stars refunds (refunded_payment) must revoke Pro, same
    as TZ-061 did for YuKassa's refund.succeeded — the bot previously had no
    handler for this event at all, and activate didn't even persist a Payment
    row for Stars purchases to look up."""

    async def _pay_and_activate(self, client, user, charge_id, internal_headers, product="pro_month"):
        res = await client.post("/v1/payments/stars/activate", headers=internal_headers,
                                json={"payload": f"{product}_{user.id}",
                                      "telegram_payment_charge_id": charge_id})
        assert res.status_code == 200

    async def test_stars_refund_requires_internal_token(self, client):
        res = await client.post("/v1/payments/stars/refund",
                                json={"telegram_payment_charge_id": "tg-x"})
        assert res.status_code == 403

    async def test_stars_refund_full_cycle_revokes_pro(self, client, auth_user, internal_headers):
        user, _ = auth_user
        await self._pay_and_activate(client, user, "tg-refund-1", internal_headers)

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "pro"

        res = await client.post("/v1/payments/stars/refund", headers=internal_headers,
                                json={"telegram_payment_charge_id": "tg-refund-1"})
        assert res.status_code == 200

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"
            assert u.subscription_expires_at is None
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "tg-refund-1"))
            assert result.first().status == "refunded"

    async def test_stars_refund_idempotent_on_retry(self, client, auth_user, internal_headers):
        user, _ = auth_user
        await self._pay_and_activate(client, user, "tg-refund-retry-1", internal_headers)

        res1 = await client.post("/v1/payments/stars/refund", headers=internal_headers,
                                 json={"telegram_payment_charge_id": "tg-refund-retry-1"})
        assert res1.status_code == 200
        res2 = await client.post("/v1/payments/stars/refund", headers=internal_headers,
                                 json={"telegram_payment_charge_id": "tg-refund-retry-1"})
        assert res2.status_code == 200

        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.subscription_tier == "free"
            assert u.subscription_expires_at is None
            result = await s.exec(select(Payment).where(Payment.provider_payment_id == "tg-refund-retry-1"))
            assert result.first().status == "refunded"

    async def test_stars_refund_unknown_payment_does_not_crash(self, client, internal_headers):
        res = await client.post("/v1/payments/stars/refund", headers=internal_headers,
                                json={"telegram_payment_charge_id": "tg-does-not-exist"})
        assert res.status_code == 404
