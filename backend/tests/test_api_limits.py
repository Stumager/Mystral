class TestHoroscope:
    async def test_horoscope_stream_authenticated(self, client, auth_headers):
        res = await client.post("/v1/horoscope/stream", headers=auth_headers,
                                json={"sign": "scorpio", "lang": "ru"})
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/event-stream")

    async def test_horoscope_stream_unauthenticated(self, client):
        res = await client.post("/v1/horoscope/stream", json={"sign": "scorpio", "lang": "ru"})
        assert res.status_code == 401

    async def test_horoscope_invalid_sign_rejected(self, client, auth_headers):
        """Unvalidated sign values would stuff the Redis cache and burn Groq quota."""
        res = await client.post("/v1/horoscope/stream", headers=auth_headers,
                                json={"sign": "<script>alert(1)</script>", "lang": "ru"})
        assert res.status_code == 422

    async def test_horoscope_scores_valid(self, client):
        res = await client.get("/v1/horoscope/scores?sign=leo")
        assert res.status_code == 200
        body = res.json()
        assert set(body) == {"love", "career", "health"}
        assert all(55 <= v <= 95 for v in body.values())

    async def test_horoscope_scores_invalid_sign(self, client):
        res = await client.get("/v1/horoscope/scores?sign=dragon")
        assert res.status_code == 422


class TestTarotLimits:
    async def test_tarot_free_limit(self, client, auth_headers):
        first = await client.post("/v1/tarot/spread", headers=auth_headers,
                                  json={"spread_id": "card_of_day"})
        assert first.status_code == 200
        assert len(first.json()["cards"]) == 1

        second = await client.post("/v1/tarot/spread", headers=auth_headers,
                                   json={"spread_id": "card_of_day"})
        assert second.status_code == 402

    async def test_tarot_pro_spread_blocked_for_free(self, client, auth_headers):
        res = await client.post("/v1/tarot/spread", headers=auth_headers,
                                json={"spread_id": "celtic_cross"})
        assert res.status_code == 402

    async def test_tarot_pro_unlimited(self, client, pro_headers):
        for _ in range(3):
            res = await client.post("/v1/tarot/spread", headers=pro_headers,
                                    json={"spread_id": "card_of_day"})
            assert res.status_code == 200

    async def test_tarot_unknown_spread(self, client, auth_headers):
        res = await client.post("/v1/tarot/spread", headers=auth_headers,
                                json={"spread_id": "fake_spread"})
        assert res.status_code == 422


class TestRunesLimits:
    async def test_runes_free_daily_limit(self, client, auth_headers):
        first = await client.post("/v1/runes/draw", headers=auth_headers,
                                  json={"spread_type": "rune_of_day"})
        assert first.status_code == 200
        second = await client.post("/v1/runes/draw", headers=auth_headers,
                                   json={"spread_type": "rune_of_day"})
        assert second.status_code == 402

    async def test_runes_pro_spread_blocked_for_free(self, client, auth_headers):
        res = await client.post("/v1/runes/draw", headers=auth_headers,
                                json={"spread_type": "yggdrasil"})
        assert res.status_code == 402


class TestAdminAuth:
    async def test_admin_without_token(self, client):
        res = await client.get("/v1/admin/stats")
        assert res.status_code == 403

    async def test_admin_with_wrong_token(self, client):
        res = await client.get("/v1/admin/stats", headers={"X-Admin-Token": "wrong"})
        assert res.status_code == 403

    async def test_admin_with_correct_token(self, client, admin_headers):
        res = await client.get("/v1/admin/stats", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert "total_users" in body

    async def test_admin_users_no_password_hash_leak(self, client, admin_headers, auth_user):
        res = await client.get("/v1/admin/users", headers=admin_headers)
        assert res.status_code == 200
        assert "password_hash" not in res.text
        assert "verification_code" not in res.text


class TestCompatibility:
    async def test_composite_requires_pro(self, client, auth_headers):
        res = await client.post("/v1/compatibility/composite", headers=auth_headers,
                                json={"partner_id": "00000000-0000-0000-0000-000000000000"})
        assert res.status_code == 402

    async def test_partners_crud(self, client, auth_headers):
        created = await client.post("/v1/partners", headers=auth_headers,
                                    json={"name": "Оксана", "birth_date": "1998-04-02"})
        assert created.status_code == 200
        listing = await client.get("/v1/partners", headers=auth_headers)
        assert listing.status_code == 200
        partners = listing.json()
        assert len(partners) == 1
        assert partners[0]["name"] == "Оксана"

        deleted = await client.delete(f"/v1/partners/{partners[0]['id']}", headers=auth_headers)
        assert deleted.status_code == 200

    async def test_partners_free_limit_3(self, client, auth_headers):
        for i in range(3):
            res = await client.post("/v1/partners", headers=auth_headers,
                                    json={"name": f"P{i}", "birth_date": "1990-01-01"})
            assert res.status_code == 200
        res = await client.post("/v1/partners", headers=auth_headers,
                                json={"name": "P4", "birth_date": "1990-01-01"})
        assert res.status_code == 402
