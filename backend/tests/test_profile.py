from app.core.database import AsyncSessionLocal
from app.models.user import User
from tests.conftest import make_user


class TestProfile:
    async def test_get_profile_authenticated(self, client, auth_headers):
        res = await client.get("/v1/profile", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert "birth_date" in body
        assert "completion_percent" in body
        # sensitive fields must never leak
        assert "push_subscription" not in body

    async def test_get_profile_unauthenticated(self, client):
        res = await client.get("/v1/profile")
        assert res.status_code == 401

    async def test_update_profile_success(self, client, auth_headers):
        res = await client.put("/v1/profile", headers=auth_headers,
                               json={"birth_date": "1990-05-15", "birth_time": "14:30",
                                     "birth_city": "Москва"})
        assert res.status_code == 200
        body = res.json()
        assert body["birth_date"] == "1990-05-15"
        assert body["birth_time"] == "14:30"

    async def test_update_profile_invalid_date(self, client, auth_headers):
        res = await client.put("/v1/profile", headers=auth_headers,
                               json={"birth_date": "15.05.1990"})
        assert res.status_code == 422

    async def test_update_profile_invalid_timezone(self, client, auth_headers):
        res = await client.put("/v1/profile", headers=auth_headers,
                               json={"timezone": "Mars/Olympus"})
        assert res.status_code == 400

    async def test_toggle_notifications_requires_internal_token(self, client):
        res = await client.post("/v1/profile/toggle-notifications",
                                json={"telegram_id": "12345"})
        assert res.status_code == 403


class TestReferrals:
    async def test_referral_my_generates_code(self, client, auth_headers):
        res = await client.get("/v1/referrals/my", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert len(body["ref_code"]) == 8
        assert body["ref_url"].endswith(body["ref_code"])

    async def test_referral_apply_success(self, client):
        referrer, ref_headers = await make_user(email="referrer@test.com")
        referred, red_headers = await make_user(email="referred@test.com")

        code = (await client.get("/v1/referrals/my", headers=ref_headers)).json()["ref_code"]
        res = await client.post("/v1/referrals/apply", headers=red_headers,
                                json={"ref_code": code})
        assert res.status_code == 200
        assert res.json()["bonus_days"] == 3

        async with AsyncSessionLocal() as s:
            rd = await s.get(User, referred.id)
            rr = await s.get(User, referrer.id)
            assert rd.subscription_tier == "pro"  # 3 bonus days
            assert rr.subscription_tier == "pro"  # 7 bonus days
            assert rd.referred_by == referrer.id

    async def test_referral_apply_self(self, client, auth_headers):
        code = (await client.get("/v1/referrals/my", headers=auth_headers)).json()["ref_code"]
        res = await client.post("/v1/referrals/apply", headers=auth_headers,
                                json={"ref_code": code})
        assert res.status_code == 400

    async def test_referral_apply_twice(self, client):
        _, ref_headers = await make_user(email="r1@test.com")
        _, red_headers = await make_user(email="r2@test.com")
        _, ref2_headers = await make_user(email="r3@test.com")

        code1 = (await client.get("/v1/referrals/my", headers=ref_headers)).json()["ref_code"]
        code2 = (await client.get("/v1/referrals/my", headers=ref2_headers)).json()["ref_code"]

        first = await client.post("/v1/referrals/apply", headers=red_headers, json={"ref_code": code1})
        assert first.status_code == 200
        second = await client.post("/v1/referrals/apply", headers=red_headers, json={"ref_code": code2})
        assert second.status_code == 400

    async def test_referral_apply_unknown_code(self, client, auth_headers):
        res = await client.post("/v1/referrals/apply", headers=auth_headers,
                                json={"ref_code": "NOPENOPE"})
        assert res.status_code == 404
