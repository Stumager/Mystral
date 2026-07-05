"""TZ-055: local birth time must be converted to UTC via the birth
location's real historical IANA timezone before ephemeris/house
calculation. Regression cases for the bug where tz_str="UTC" was
hardcoded, silently treating local time as if it were already UTC.

Needs the real kerykeion + pyswisseph stack (no Windows wheel), so these
run for real only in Docker/Linux; they skip everywhere else instead of
hitting the local test stub (see tests/conftest.py).
"""
import pytest

try:
    import swisseph  # noqa: F401
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False

pytestmark = pytest.mark.skipif(
    not HAS_SWISSEPH,
    reason="pyswisseph has no Windows wheel; real ephemeris only available in Docker/Linux",
)


def _chart(year, month, day, hour, minute, lat, lon):
    from app.api.v1.natal import _build_subject, build_full_chart
    subj = _build_subject("TZ-055", year, month, day, hour, minute, lat, lon)
    return subj, build_full_chart(subj)


def _planet(chart, name):
    return next(p for p in chart["planets"] if p["name"] == name)


def test_timezone_conversion_belorechensk_2003():
    """Control case 1: Belorechensk, 18.11.2003 02:30 (Europe/Moscow, UTC+3
    in Nov 2003 - winter time). Values per TZ-055 control calculation."""
    subj, chart = _chart(2003, 11, 18, 2, 30, 44.76, 39.87)

    assert subj.tz_str == "Europe/Moscow"

    assert chart["ascendant"]["sign"] == "Virgo"
    assert chart["ascendant"]["degree"] == pytest.approx(29.2, abs=0.15)
    assert chart["midheaven"]["sign"] == "Gemini"
    assert chart["midheaven"]["degree"] == pytest.approx(29.1, abs=0.15)

    expected = {
        "sun": ("Scorpio", 25.2, False),
        "moon": ("Virgo", 4.9, False),
        "mercury": ("Sagittarius", 8.6, False),
        "venus": ("Sagittarius", 18.7, False),
        "mars": ("Pisces", 14.7, False),
        "jupiter": ("Virgo", 15.6, False),
        "saturn": ("Cancer", 12.8, True),
        "uranus": ("Aquarius", 28.9, False),
        "neptune": ("Aquarius", 10.6, False),
        "pluto": ("Sagittarius", 18.9, False),
    }
    for name, (sign, degree, retro) in expected.items():
        p = _planet(chart, name)
        assert p["sign"] == sign, f"{name}: expected sign {sign}, got {p['sign']}"
        assert p["degree"] == pytest.approx(degree, abs=0.15), f"{name}: expected ~{degree}°, got {p['degree']}"
        assert p["retrograde"] is retro, f"{name}: expected retrograde={retro}"


def test_timezone_conversion_tula_2005_dst():
    """Control case 2: Tula, 28.03.2005 18:30. Russian DST started
    27.03.2005, so this date is already UTC+4 - a hardcoded "Russia =
    UTC+3" fix would get this one wrong (Libra instead of Virgo Ascendant),
    proving the fix must use real historical tzdata, not a fixed offset."""
    subj, chart = _chart(2005, 3, 28, 18, 30, 54.2, 37.6)

    assert subj.tz_str == "Europe/Moscow"

    assert chart["ascendant"]["sign"] == "Virgo"
    assert chart["ascendant"]["degree"] == pytest.approx(24.0, abs=0.15)
    assert chart["midheaven"]["sign"] == "Gemini"
    assert chart["midheaven"]["degree"] == pytest.approx(21.9, abs=0.15)

    sun = _planet(chart, "sun")
    assert sun["sign"] == "Aries"
    assert sun["degree"] == pytest.approx(8.0, abs=0.15)

    moon = _planet(chart, "moon")
    assert moon["sign"] == "Scorpio"
    assert moon["degree"] == pytest.approx(11.1, abs=0.15)
