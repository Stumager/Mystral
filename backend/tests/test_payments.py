from datetime import datetime, timedelta

from app.core.database import AsyncSessionLocal
from app.models.user import User
from tests.conftest import make_user


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
