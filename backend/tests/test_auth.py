from datetime import datetime, timedelta

from sqlmodel import select

from app.core.database import AsyncSessionLocal
from app.models.user import AuthProvider, User
from tests.conftest import make_user


async def _get_user(email: str) -> User:
    async with AsyncSessionLocal() as s:
        return (await s.exec(select(User).where(User.email == email))).first()


REG = {"email": "new@test.com", "password": "Password1", "name": "New"}


class TestRegister:
    async def test_register_success(self, client):
        res = await client.post("/v1/auth/register", json=REG)
        assert res.status_code == 200
        assert res.json()["status"] == "verification_required"
        user = await _get_user("new@test.com")
        assert user is not None
        assert user.email_verified is False
        assert user.verification_code is not None

    async def test_register_duplicate_email(self, client):
        await client.post("/v1/auth/register", json=REG)
        res = await client.post("/v1/auth/register", json=REG)
        assert res.status_code == 400

    async def test_register_weak_password(self, client):
        for bad in ["short1A", "nouppercase1", "NoDigitsHere"]:
            res = await client.post("/v1/auth/register", json={**REG, "password": bad})
            assert res.status_code == 400, bad

    async def test_register_invalid_email(self, client):
        res = await client.post("/v1/auth/register", json={**REG, "email": "not-an-email"})
        assert res.status_code == 400

    async def test_register_invalid_names_rejected_empty_and_short(self, client):
        """TZ-059: name wasn't validated for real beyond non-empty + max-100.
        Split from the other invalid-names test to stay under the 5/hour
        per-IP register rate limit (_check_ip_rate)."""
        bad_names = [
            "",              # empty
            "   ",           # whitespace only (trims to empty)
            "A",             # 1 char, below the 2-char minimum
        ]
        for i, bad in enumerate(bad_names):
            res = await client.post("/v1/auth/register",
                                    json={**REG, "email": f"badname-a{i}@test.com", "name": bad})
            assert res.status_code == 400, f"expected 400 for name={bad!r}, got {res.status_code}"

    async def test_register_invalid_names_rejected_special_and_long(self, client):
        bad_names = [
            "!!!",           # punctuation only, no letter
            "A" * 51,        # over the 50-char maximum
            "<script>",      # HTML tag, XSS risk in share cards/emails/profile
        ]
        for i, bad in enumerate(bad_names):
            res = await client.post("/v1/auth/register",
                                    json={**REG, "email": f"badname-b{i}@test.com", "name": bad})
            assert res.status_code == 400, f"expected 400 for name={bad!r}, got {res.status_code}"

    async def test_register_valid_names_with_punctuation_allowed(self, client):
        """Space/hyphen/apostrophe inside a name must not be blocked, and any
        of the platform's 6 languages' alphabets must count as a letter —
        not a hardcoded Latin/Cyrillic-only check."""
        good_names = ["O'Brien", "Anne-Marie", "Анна", "Ana María", "Ali"]
        for i, good in enumerate(good_names):
            res = await client.post("/v1/auth/register",
                                    json={**REG, "email": f"goodname{i}@test.com", "name": good})
            assert res.status_code == 200, f"expected 200 for name={good!r}, got {res.status_code}: {res.text}"

    async def test_register_name_is_trimmed_before_storage(self, client):
        res = await client.post("/v1/auth/register",
                                json={**REG, "email": "trimname@test.com", "name": "  Anna  "})
        assert res.status_code == 200
        user = await _get_user("trimname@test.com")
        assert user.display_name == "Anna"


class TestLogin:
    async def test_login_success(self, client):
        await make_user(email="login@test.com", password="Password1")
        res = await client.post("/v1/auth/login", json={"email": "login@test.com", "password": "Password1"})
        assert res.status_code == 200
        body = res.json()
        assert body["access_token"]
        assert body["user"]["name"] == "Test"

    async def test_login_wrong_password(self, client):
        await make_user(email="login2@test.com")
        res = await client.post("/v1/auth/login", json={"email": "login2@test.com", "password": "Wrong111"})
        assert res.status_code == 401

    async def test_login_unknown_email(self, client):
        res = await client.post("/v1/auth/login", json={"email": "ghost@test.com", "password": "Password1"})
        assert res.status_code == 401

    async def test_login_rate_limit(self, client):
        await make_user(email="rl@test.com")
        last = None
        for _ in range(11):
            last = await client.post("/v1/auth/login", json={"email": "rl@test.com", "password": "Wrong111"})
        assert last.status_code == 429


class TestVerifyEmail:
    async def _register(self, client, email="v@test.com"):
        await client.post("/v1/auth/register", json={**REG, "email": email})
        return await _get_user(email)

    async def test_verify_email_success(self, client):
        user = await self._register(client)
        res = await client.post("/v1/auth/verify-email",
                                json={"email": user.email, "code": user.verification_code})
        assert res.status_code == 200
        assert res.json()["access_token"]
        assert (await _get_user(user.email)).email_verified is True

    async def test_verify_email_wrong_code(self, client):
        user = await self._register(client)
        wrong = "000000" if user.verification_code != "000000" else "111111"
        res = await client.post("/v1/auth/verify-email", json={"email": user.email, "code": wrong})
        assert res.status_code == 400

    async def test_verify_email_expired(self, client):
        user = await self._register(client)
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            u.verification_code_expires_at = datetime.utcnow() - timedelta(minutes=1)
            s.add(u)
            await s.commit()
        res = await client.post("/v1/auth/verify-email",
                                json={"email": user.email, "code": user.verification_code})
        assert res.status_code == 400

    async def test_verify_email_bruteforce_locked(self, client):
        """5 wrong attempts invalidate the code entirely."""
        user = await self._register(client)
        wrong = "000000" if user.verification_code != "000000" else "111111"
        for _ in range(5):
            await client.post("/v1/auth/verify-email", json={"email": user.email, "code": wrong})
        res = await client.post("/v1/auth/verify-email",
                                json={"email": user.email, "code": user.verification_code})
        assert res.status_code == 400  # real code no longer works


class TestPasswordReset:
    async def test_forgot_password_success(self, client):
        await make_user(email="fp@test.com")
        res = await client.post("/v1/auth/forgot-password", json={"email": "fp@test.com"})
        assert res.status_code == 200
        user = await _get_user("fp@test.com")
        assert user.reset_token is not None

    async def test_forgot_password_unknown_email_no_leak(self, client):
        res = await client.post("/v1/auth/forgot-password", json={"email": "ghost@test.com"})
        assert res.status_code == 200  # same response — no user enumeration

    async def test_reset_password_success(self, client):
        await make_user(email="rp@test.com")
        await client.post("/v1/auth/forgot-password", json={"email": "rp@test.com"})
        user = await _get_user("rp@test.com")
        res = await client.post("/v1/auth/reset-password",
                                json={"token": user.reset_token, "new_password": "NewPassword1"})
        assert res.status_code == 200
        login = await client.post("/v1/auth/login",
                                  json={"email": "rp@test.com", "password": "NewPassword1"})
        assert login.status_code == 200

    async def test_reset_password_invalid_token(self, client):
        res = await client.post("/v1/auth/reset-password",
                                json={"token": "bogus", "new_password": "NewPassword1"})
        assert res.status_code == 400


class TestChangePassword:
    async def test_change_password_success(self, client):
        _, headers = await make_user(email="cp@test.com")
        res = await client.post("/v1/auth/change-password", headers=headers,
                                json={"current_password": "Password1", "new_password": "NewPassword1"})
        assert res.status_code == 200
        login = await client.post("/v1/auth/login",
                                  json={"email": "cp@test.com", "password": "NewPassword1"})
        assert login.status_code == 200

    async def test_change_password_wrong_current(self, client):
        _, headers = await make_user(email="cp2@test.com")
        res = await client.post("/v1/auth/change-password", headers=headers,
                                json={"current_password": "Wrong111", "new_password": "NewPassword1"})
        assert res.status_code == 400


class TestDeleteAccount:
    async def test_delete_account_scheduled(self, client):
        user, headers = await make_user(email="del@test.com")
        res = await client.request("DELETE", "/v1/auth/account", headers=headers,
                                   json={"password": "Password1"})
        assert res.status_code == 200
        assert res.json()["status"] == "scheduled"
        async with AsyncSessionLocal() as s:
            u = await s.get(User, user.id)
            assert u.is_active is False
            assert u.deletion_scheduled_at is not None

    async def test_delete_account_wrong_password(self, client):
        _, headers = await make_user(email="del2@test.com")
        res = await client.request("DELETE", "/v1/auth/account", headers=headers,
                                   json={"password": "Wrong111"})
        assert res.status_code == 400

    async def test_deactivated_token_rejected(self, client):
        """After deletion is scheduled the old JWT must stop working."""
        _, headers = await make_user(email="del3@test.com")
        await client.request("DELETE", "/v1/auth/account", headers=headers,
                             json={"password": "Password1"})
        res = await client.get("/v1/auth/me", headers=headers)
        assert res.status_code == 401

    async def test_login_reactivates_account(self, client):
        _, headers = await make_user(email="del4@test.com")
        await client.request("DELETE", "/v1/auth/account", headers=headers,
                             json={"password": "Password1"})
        res = await client.post("/v1/auth/login",
                                json={"email": "del4@test.com", "password": "Password1"})
        assert res.status_code == 200
        user = await _get_user("del4@test.com")
        assert user.is_active is True
        assert user.deletion_scheduled_at is None


class TestLogout:
    async def test_logout_blacklists_token(self, client):
        _, headers = await make_user(email="lo@test.com")
        assert (await client.get("/v1/auth/me", headers=headers)).status_code == 200
        res = await client.post("/v1/auth/logout", headers=headers)
        assert res.status_code == 200
        assert (await client.get("/v1/auth/me", headers=headers)).status_code == 401


class TestMe:
    async def test_me_authenticated(self, client, auth_headers):
        res = await client.get("/v1/auth/me", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert "password" not in str(body).lower() or "password_hash" not in body

    async def test_me_unauthenticated(self, client):
        res = await client.get("/v1/auth/me")
        assert res.status_code == 401
