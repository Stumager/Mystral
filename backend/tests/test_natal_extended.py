"""TZ-103: house systems, optional points, minor aspects.

Step 0 of the ticket was an audit of what kerykeion 4.14 already does, and
the answers shape most of these tests:

  * Placidus was already the library default, so the no-argument path must
    keep producing exactly the cusps it did before this ticket — that's the
    regression this file guards hardest.
  * Lilith, Chiron and both nodes are computed on every subject regardless;
    the ticket's "optional points" are a read/filter concern, not a
    calculation one.
  * Ceres/Pallas/Juno/Vesta are NOT in kerykeion's Planet literal, but the
    ephemeris file covering them (seas_18.se1) ships inside the package, so
    they're reachable through swisseph with kerykeion's own julian_day.
    The reference longitudes below come from that ephemeris.
  * kerykeion does have an aspect engine, but its matcher truncates the
    angular distance with int() before comparing against the orb, which
    widens every orb by up to a degree on one side only — see
    TestMinorAspectOrbsAreExact. That's why the exact float comparison in
    _calc_aspects stays.
"""
from datetime import date
from unittest.mock import patch

import pytest

from app.api.v1.natal import (
    ALL_ASPECT_TYPES,
    ASPECT_CATEGORY,
    ASPECT_NAMES_I18N,
    ASPECT_TYPES,
    AVAILABLE_POINTS,
    DEFAULT_HOUSE_SYSTEM,
    DEFAULT_POINTS,
    HOUSE_SYSTEMS,
    MINOR_ASPECT_TYPES,
    PLANET_NAMES_EN,
    PLANET_NAMES_RU,
    PLANET_SYMBOLS,
    _build_subject,
    _calc_aspects,
    _house_for,
    build_full_chart,
)

try:
    import swisseph  # noqa: F401
    HAS_EPHEMERIS = True
except ImportError:  # pragma: no cover — Windows dev box
    HAS_EPHEMERIS = False

# conftest.py stubs kerykeion when pyswisseph is missing (no Windows wheel),
# which is why the rest of this suite never asserts astro math. TZ-103 is
# astro math, so these classes are marked instead of weakened: they run for
# real in the Docker image, and skip on a local Windows checkout rather than
# pretending to pass there.
requires_ephemeris = pytest.mark.skipif(
    not HAS_EPHEMERIS, reason="needs the real pyswisseph/kerykeion (Docker image)")

# 15 May 1990, 14:30 Moscow — the date used throughout the step 0 audit.
BIRTH = dict(year=1990, month=5, day=15, hour=14, minute=30, lat=55.75, lon=37.61)
BODY = {"name": "Test", "year": 1990, "month": 5, "day": 15, "hour": 14,
        "minute": 30, "city": "Moscow"}


def _subject(house_system=DEFAULT_HOUSE_SYSTEM):
    return _build_subject("Test", BIRTH["year"], BIRTH["month"], BIRTH["day"],
                          BIRTH["hour"], BIRTH["minute"], BIRTH["lat"], BIRTH["lon"],
                          house_system=house_system)


@requires_ephemeris
class TestHouseSystems:
    def test_placidus_is_the_default_and_the_library_agrees(self):
        """Both halves matter: that we default to P, and that kerykeion
        resolves P to Placidus rather than us just labelling it so."""
        subj = _subject()
        assert DEFAULT_HOUSE_SYSTEM == "P"
        assert subj.houses_system_identifier == "P"
        assert subj.houses_system_name == "Placidus"

    def test_every_offered_system_is_accepted_by_the_library(self):
        for code, name in HOUSE_SYSTEMS.items():
            subj = _subject(code)
            assert subj.houses_system_identifier == code, code
            assert subj.houses_system_name, code

    def test_switching_system_moves_intermediate_cusps_but_not_the_angles(self):
        """Placidus and Koch are both quadrant systems: they split the
        quadrants differently but share the Ascendant and the MC. If a
        refactor ever swapped in a non-quadrant system by accident, this
        catches it."""
        placidus = build_full_chart(_subject("P"))
        koch = build_full_chart(_subject("K"))
        assert placidus["ascendant"]["abs_pos"] == koch["ascendant"]["abs_pos"]
        assert placidus["midheaven"]["abs_pos"] == koch["midheaven"]["abs_pos"]
        assert placidus["houses"][1]["abs_pos"] != koch["houses"][1]["abs_pos"]

    def test_equal_houses_are_thirty_degrees_apart_from_the_ascendant(self):
        chart = build_full_chart(_subject("A"))
        asc = chart["ascendant"]["abs_pos"]
        for h in chart["houses"]:
            expected = (asc + (h["number"] - 1) * 30) % 360
            assert abs(h["abs_pos"] - expected) < 0.2, h["number"]

    def test_midheaven_is_the_real_mc_not_the_tenth_cusp(self):
        """In Equal houses cusp 10 is just Ascendant + 270°, which is not the
        Midheaven. The MC axis has to stay astronomically correct whichever
        house system is selected, so it can't be read off cusp 10."""
        equal = build_full_chart(_subject("A"))
        placidus = build_full_chart(_subject("P"))
        assert equal["midheaven"]["abs_pos"] == placidus["midheaven"]["abs_pos"]
        tenth_cusp = equal["houses"][9]["abs_pos"]
        assert abs(tenth_cusp - equal["midheaven"]["abs_pos"]) > 1

    def test_quadrant_systems_put_the_mc_on_cusp_ten(self):
        for code in ("P", "K", "C", "R"):
            chart = build_full_chart(_subject(code))
            assert abs(chart["houses"][9]["abs_pos"] - chart["midheaven"]["abs_pos"]) < 0.2, code

    def test_chart_reports_back_the_system_actually_used(self):
        chart = build_full_chart(_subject("C"))
        assert chart["house_system"] == {"code": "C", "name": "Campanus"}


@requires_ephemeris
class TestOptionalPoints:
    def test_default_set_covers_the_points_the_ticket_calls_mandatory(self):
        for key in ("nodes", "lilith", "chiron"):
            assert key in DEFAULT_POINTS

    def test_asteroids_are_available_but_off_by_default(self):
        for key in ("ceres", "pallas", "juno", "vesta"):
            assert key in AVAILABLE_POINTS
            assert key not in DEFAULT_POINTS

    def test_default_chart_has_nodes_lilith_chiron_and_no_asteroids(self):
        names = {p["name"] for p in build_full_chart(_subject())["extra_points"]}
        assert {"true_node", "south_node", "lilith", "chiron"} <= names
        assert names.isdisjoint({"ceres", "pallas", "juno", "vesta"})

    def test_asteroids_appear_when_asked_for(self):
        chart = build_full_chart(_subject(), points=["ceres", "pallas", "juno", "vesta"])
        names = [p["name"] for p in chart["extra_points"]]
        assert names == ["ceres", "pallas", "juno", "vesta"]

    def test_asteroid_longitudes_match_the_bundled_ephemeris(self):
        chart = build_full_chart(_subject(), points=["ceres", "pallas", "juno", "vesta"])
        by_name = {p["name"]: p for p in chart["extra_points"]}
        # Longitudes read from kerykeion's own seas_18.se1 for this instant.
        for name, expected in (("ceres", 105.2), ("pallas", 58.4),
                               ("juno", 225.6), ("vesta", 21.6)):
            assert abs(by_name[name]["abs_pos"] - expected) < 0.2, name
        # Juno is the one retrograde body of the four on this date, which is
        # also a check that the speed flag is actually being read.
        assert by_name["juno"]["retrograde"] is True
        assert by_name["vesta"]["retrograde"] is False

    def test_every_point_carries_the_same_fields_as_a_planet(self):
        chart = build_full_chart(_subject(), points=AVAILABLE_POINTS)
        for p in chart["extra_points"] + [chart["part_of_fortune"]]:
            for field in ("name", "name_ru", "name_en", "name_local", "symbol",
                          "sign", "sign_ru", "sign_local", "degree", "abs_pos",
                          "house", "retrograde", "type"):
                assert field in p, (p["name"], field)

    def test_south_node_is_opposite_the_north_node(self):
        by_name = {p["name"]: p for p in build_full_chart(_subject())["extra_points"]}
        diff = (by_name["south_node"]["abs_pos"] - by_name["true_node"]["abs_pos"]) % 360
        assert abs(diff - 180) < 0.2

    def test_points_can_be_switched_off_entirely(self):
        chart = build_full_chart(_subject(), points=[])
        assert chart["extra_points"] == []
        assert chart["part_of_fortune"] is None
        assert chart["points_included"] == []

    def test_optional_points_get_a_house_from_the_selected_system(self):
        """The bodies we read straight out of swisseph have no house of their
        own — _house_for assigns one, so it must follow the chosen system."""
        placidus = build_full_chart(_subject("P"), points=["ceres"])
        whole = build_full_chart(_subject("A"), points=["ceres"])
        assert placidus["extra_points"][0]["house"] is not None
        assert whole["extra_points"][0]["house"] is not None

    def test_new_points_have_names_and_glyphs_in_both_base_languages(self):
        for key in ("lilith", "ceres", "pallas", "juno", "vesta", "part_of_fortune", "south_node"):
            assert PLANET_NAMES_RU[key]
            assert PLANET_NAMES_EN[key]
            assert PLANET_SYMBOLS[key]

    def test_luminaries_use_glyphs_not_emoji(self):
        """The Sun and Moon were the only two rendered as colour emoji."""
        assert PLANET_SYMBOLS["sun"] == "☉"
        assert PLANET_SYMBOLS["moon"] == "☽"


class TestHouseForHelper:
    HOUSES = [{"number": i + 1, "abs_pos": (i * 30 + 350) % 360} for i in range(12)]

    def test_finds_the_containing_house(self):
        assert _house_for(355.0, self.HOUSES) == 1
        assert _house_for(25.0, self.HOUSES) == 2

    def test_handles_the_zero_degree_wrap(self):
        """House 1 here starts at 350° and ends at 20°, i.e. it straddles the
        0°/360° seam — the case a naive start <= x < end comparison drops."""
        assert _house_for(5.0, self.HOUSES) == 1

    def test_returns_none_for_an_incomplete_cusp_list(self):
        assert _house_for(10.0, self.HOUSES[:5]) is None


class TestMinorAspects:
    def test_minor_table_covers_the_standard_set(self):
        types = {a[2] for a in MINOR_ASPECT_TYPES}
        assert types == {"semisextile", "semisquare", "quintile",
                         "sesquiquadrate", "biquintile", "quincunx"}

    def test_minor_table_keeps_the_major_tuple_shape(self):
        """compatibility.py imports ASPECT_TYPES and unpacks it positionally;
        the two lists have to stay structurally interchangeable."""
        for entry in MINOR_ASPECT_TYPES:
            assert len(entry) == len(ASPECT_TYPES[0])

    def test_every_aspect_has_a_category(self):
        for _, _, atype, _, _, _ in ALL_ASPECT_TYPES:
            assert atype in ASPECT_CATEGORY

    def test_categories_follow_the_reference_convention(self):
        assert ASPECT_CATEGORY["square"] == "tense"
        assert ASPECT_CATEGORY["opposition"] == "tense"
        assert ASPECT_CATEGORY["trine"] == "harmonious"
        assert ASPECT_CATEGORY["sextile"] == "harmonious"
        assert ASPECT_CATEGORY["quincunx"] == "minor"
        assert ASPECT_CATEGORY["semisextile"] == "minor"
        assert ASPECT_CATEGORY["conjunction"] == "neutral"

    def test_every_aspect_is_named_in_every_language(self):
        for _, _, atype, name_ru, name_en, _ in ALL_ASPECT_TYPES:
            assert name_ru and name_en and name_ru != name_en
            for lang in ("es", "pt", "tr", "uk"):
                assert ASPECT_NAMES_I18N[lang].get(atype), (lang, atype)

    def test_minor_aspects_are_detected(self):
        p1 = {"name": "sun", "name_ru": "Солнце", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "abs_pos": 150.0}
        aspects = _calc_aspects([p1, p2])
        assert aspects[0]["type"] == "quincunx"
        assert aspects[0]["category"] == "minor"
        assert aspects[0]["is_major"] is False

    def test_minor_aspects_can_be_excluded(self):
        p1 = {"name": "sun", "name_ru": "Солнце", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "abs_pos": 150.0}
        assert _calc_aspects([p1, p2], include_minor=False) == []

    def test_majors_keep_their_existing_orbs(self):
        """Widening the aspect table must not quietly change which major
        aspects existing users see."""
        p1 = {"name": "sun", "name_ru": "Солнце", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "abs_pos": 127.9}
        assert _calc_aspects([p1, p2])[0]["type"] == "trine"
        p2["abs_pos"] = 128.1
        assert _calc_aspects([p1, p2]) == []

    @pytest.mark.parametrize("distance,expected", [
        (30.0, "semisextile"),
        (30.9, "semisextile"),
        (31.1, None),
        (31.9, None),
    ])
    def test_minor_aspect_orbs_are_exact(self, distance, expected):
        """kerykeion's own matcher does int(distance) before comparing, so it
        calls 31.9° a 1°-orb semisextile. Ours compares the float, so 31.1°
        is already out of orb."""
        p1 = {"name": "sun", "name_ru": "Солнце", "abs_pos": 0.0}
        p2 = {"name": "moon", "name_ru": "Луна", "abs_pos": distance}
        aspects = _calc_aspects([p1, p2])
        assert (aspects[0]["type"] if aspects else None) == expected

    @requires_ephemeris
    def test_aspect_grid_spans_the_optional_points(self):
        chart = build_full_chart(_subject(), points=["chiron", "lilith", "nodes"])
        named = {a["planet1"] for a in chart["aspects"]} | {a["planet2"] for a in chart["aspects"]}
        assert "chiron" in named

    @requires_ephemeris
    def test_south_node_is_kept_out_of_the_aspect_grid(self):
        """It sits exactly 180° from the North Node by construction, so every
        aspect it forms mirrors one already in the list."""
        chart = build_full_chart(_subject(), points=["nodes"])
        named = {a["planet1"] for a in chart["aspects"]} | {a["planet2"] for a in chart["aspects"]}
        assert "south_node" not in named
        assert "true_node" in named


@requires_ephemeris
class TestCalculateEndpoint:
    async def test_defaults_are_accepted_without_the_new_fields(self, client, auth_headers):
        """A client that predates TZ-103 sends no house_system and no points."""
        with _patched_geocode():
            res = await client.post("/v1/natal/calculate", headers=auth_headers, json=BODY)
        assert res.status_code == 200
        body = res.json()
        assert body["house_system"]["code"] == "P"
        assert "lilith" in body["points_included"]

    async def test_house_system_is_threaded_through(self, client, auth_headers):
        with _patched_geocode():
            res = await client.post("/v1/natal/calculate", headers=auth_headers,
                                    json={**BODY, "house_system": "K"})
        assert res.status_code == 200
        assert res.json()["house_system"] == {"code": "K", "name": "Koch"}

    async def test_unknown_house_system_is_rejected_before_calculating(self, client, auth_headers):
        res = await client.post("/v1/natal/calculate", headers=auth_headers,
                                json={**BODY, "house_system": "Z"})
        assert res.status_code == 422

    async def test_unknown_point_is_rejected(self, client, auth_headers):
        res = await client.post("/v1/natal/calculate", headers=auth_headers,
                                json={**BODY, "points": ["nodes", "nibiru"]})
        assert res.status_code == 422

    async def test_options_endpoint_matches_the_accepted_values(self, client, auth_headers):
        """The form builds itself from this, so it must not be able to offer
        anything /natal/calculate would then reject."""
        res = await client.get("/v1/natal/options", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert [h["code"] for h in body["house_systems"]] == list(HOUSE_SYSTEMS)
        assert body["points"] == AVAILABLE_POINTS
        assert body["default_house_system"] == DEFAULT_HOUSE_SYSTEM
        assert body["default_points"] == DEFAULT_POINTS

    async def test_options_requires_auth(self, client):
        assert (await client.get("/v1/natal/options")).status_code in (401, 403)


def _patched_geocode():
    from unittest.mock import AsyncMock, patch
    return patch("app.api.v1.natal.geocode_city", new=AsyncMock(return_value=(55.75, 37.61)))


ALL_POINTS = ["nodes", "lilith", "chiron", "part_of_fortune", "ceres", "pallas", "juno", "vesta"]


@requires_ephemeris
class TestInterpretMaxTokensScaling:
    """Sasha flagged this before commit: TZ-103 grew the 'planets' and
    'aspects' prompts (up to 8 optional points on top of the 10 planets;
    majors AND minors together instead of just the top 5 majors) without
    raising the requested word count ("150-250 слов" is unchanged). That's
    the exact shape of bug QA-015/016 found in horoscope.py — a max_tokens
    ceiling sized for the old content volume can truncate a longer real
    generation mid-sentence, even though the *target* length didn't move.
    Scaled the same way tarot.py already scales with card count, rather than
    raising every section's ceiling regardless of whether it actually grew.
    """

    async def _capture_max_tokens(self, client, headers, section, points=None):
        captured = {}

        def _capturing_stream(messages, max_tokens=900, lang="ru", on_finish=None):
            captured["max_tokens"] = max_tokens

            async def _gen():
                yield 'data: {"text": "ok"}\n\n'
                yield "data: [DONE]\n\n"
            return _gen()

        body = {**BODY, "section": section, "lang": "ru"}
        if points is not None:
            body["points"] = points
        with _patched_geocode(), patch("app.api.v1.natal.safe_groq_stream", _capturing_stream):
            res = await client.post("/v1/natal/interpret", headers=headers, json=body)
        assert res.status_code == 200, res.text
        return captured["max_tokens"]

    async def test_personality_keeps_the_existing_ceiling(self, client, pro_headers):
        assert await self._capture_max_tokens(client, pro_headers, "personality") == 1400

    async def test_houses_keeps_the_existing_ceiling(self, client, pro_headers):
        assert await self._capture_max_tokens(client, pro_headers, "houses") == 1400

    async def test_transits_keeps_the_existing_ceiling(self, client, pro_headers):
        assert await self._capture_max_tokens(client, pro_headers, "transits") == 1400

    async def test_aspects_is_raised_when_minor_aspects_are_present(self, client, pro_headers):
        """Not an edge case: on the reference test date (used throughout this
        file), the default point set already produces minor aspects among
        the ~14 bodies in play, so this is the realistic everyday case."""
        assert await self._capture_max_tokens(client, pro_headers, "aspects") == 1800

    async def test_planets_stays_at_the_existing_ceiling_by_default(self, client, pro_headers):
        """Default points (nodes+lilith+chiron+part_of_fortune) put 4 items
        in extra_points — barely more than the 3 (node+south_node+chiron)
        that were always unconditionally shown before this ticket. Not
        enough growth to warrant a higher ceiling on its own."""
        assert await self._capture_max_tokens(client, pro_headers, "planets") == 1400

    async def test_planets_is_raised_when_asteroids_are_selected(self, client, pro_headers):
        """All 8 optional points -> 8 entries in extra_points (nodes counts
        as 2), on top of the 10 planets -> 18 bodies to discuss in the same
        150-250 word budget."""
        assert await self._capture_max_tokens(client, pro_headers, "planets", points=ALL_POINTS) == 1800

    async def test_free_user_stays_paywalled_regardless_of_section(self, client, auth_headers):
        """The scaling logic runs after the paywall check — must not
        accidentally let a free user reach it by picking a specific section."""
        res = await client.post("/v1/natal/interpret", headers=auth_headers,
                                json={**BODY, "section": "aspects", "lang": "ru"})
        assert res.status_code == 402
