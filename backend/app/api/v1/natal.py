import json
import os
import tempfile
from datetime import date as date_cls, datetime
from pathlib import Path
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from kerykeion import AstrologicalSubject
from pydantic import BaseModel, Field, model_validator
from sqlmodel.ext.asyncio.session import AsyncSession
from timezonefinder import TimezoneFinder

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import lang_enforce, system_prompt
from app.core.structural_i18n import localized_field
from app.data.natal_i18n import PLANET_NAMES_I18N, SIGNS_I18N
from app.models.user import User

router = APIRouter()
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

SIGNS_RU = {
    "Ari": "Овен", "Aries": "Овен", "Tau": "Телец", "Taurus": "Телец",
    "Gem": "Близнецы", "Gemini": "Близнецы", "Can": "Рак", "Cancer": "Рак",
    "Leo": "Лев", "Vir": "Дева", "Virgo": "Дева", "Lib": "Весы", "Libra": "Весы",
    "Sco": "Скорпион", "Scorpio": "Скорпион", "Sag": "Стрелец", "Sagittarius": "Стрелец",
    "Cap": "Козерог", "Capricorn": "Козерог", "Aqu": "Водолей", "Aquarius": "Водолей",
    "Pis": "Рыбы", "Pisces": "Рыбы",
}

SIGN_ORDER = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

ELEMENTS = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}
MODALITIES = {
    "Aries": "cardinal", "Cancer": "cardinal", "Libra": "cardinal", "Capricorn": "cardinal",
    "Taurus": "fixed", "Leo": "fixed", "Scorpio": "fixed", "Aquarius": "fixed",
    "Gemini": "mutable", "Virgo": "mutable", "Sagittarius": "mutable", "Pisces": "mutable",
}

# TZ-103: the Sun and Moon were the only two drawn as colour emoji here while
# every other body used its astronomical glyph, so the planet table rendered
# with two oversized pictograms among ten monochrome symbols. Reference charts
# use ☉/☽ throughout.
PLANET_SYMBOLS = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇",
    "true_node": "☊", "south_node": "☋", "chiron": "⚷", "lilith": "⚸",
    "ceres": "⚳", "pallas": "⚴", "juno": "⚵", "vesta": "⚶",
    "part_of_fortune": "⊗",
}
PLANET_NAMES_RU = {
    "sun": "Солнце", "moon": "Луна", "mercury": "Меркурий", "venus": "Венера",
    "mars": "Марс", "jupiter": "Юпитер", "saturn": "Сатурн",
    "uranus": "Уран", "neptune": "Нептун", "pluto": "Плутон",
    "true_node": "Сев. узел", "south_node": "Юж. узел", "chiron": "Хирон",
    "lilith": "Лилит", "ceres": "Церера", "pallas": "Паллада",
    "juno": "Юнона", "vesta": "Веста", "part_of_fortune": "Часть Фортуны",
}
PLANET_NAMES_EN = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus",
    "mars": "Mars", "jupiter": "Jupiter", "saturn": "Saturn",
    "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto",
    "true_node": "North Node", "south_node": "South Node", "chiron": "Chiron",
    "lilith": "Lilith", "ceres": "Ceres", "pallas": "Pallas",
    "juno": "Juno", "vesta": "Vesta", "part_of_fortune": "Part of Fortune",
}

ASPECT_TYPES = [
    (0, 8, "conjunction", "Соединение", "Conjunction", "☌"),
    (60, 6, "sextile", "Секстиль", "Sextile", "⚹"),
    (90, 8, "square", "Квадрат", "Square", "□"),
    (120, 8, "trine", "Трин", "Trine", "△"),
    (180, 8, "opposition", "Оппозиция", "Opposition", "☍"),
]

# TZ-103. Same 6-tuple shape as ASPECT_TYPES on purpose: compatibility.py
# imports ASPECT_TYPES and unpacks it positionally for synastry, which stays
# major-only (a synastry grid with minors is unreadable), so the minor set is
# a separate list rather than extra columns on the shared one.
#
# The orbs are kerykeion's own defaults (1° for every minor aspect), not
# numbers picked by us — and a tight orb is also what the reference software
# recommends, since it explicitly advises against drawing the full minor grid
# in the wheel.
MINOR_ASPECT_TYPES = [
    (30, 1, "semisextile", "Полусекстиль", "Semisextile", "⚺"),
    (45, 1, "semisquare", "Полуквадрат", "Semisquare", "∠"),
    (72, 1, "quintile", "Квинтиль", "Quintile", "Q"),
    (135, 1, "sesquiquadrate", "Полутораквадрат", "Sesquiquadrate", "⚼"),
    (144, 1, "biquintile", "Биквинтиль", "Biquintile", "bQ"),
    (150, 1, "quincunx", "Квинконс", "Quincunx", "⚻"),
]

ALL_ASPECT_TYPES = ASPECT_TYPES + MINOR_ASPECT_TYPES

# TZ-103 step 0 — the colour convention is taken from the reference software,
# not invented: red for the analytical/tense group, blue for the harmonious
# one, green for the minor aspects. The reference names quincunx and
# semisextile as its green pair; the remaining minors join the same group
# rather than getting a fourth colour of our own. Conjunction stays neutral —
# it is neither tense nor harmonious on its own, it takes the character of
# whatever two bodies it joins.
ASPECT_CATEGORY = {
    "conjunction": "neutral",
    "sextile": "harmonious", "trine": "harmonious",
    "square": "tense", "opposition": "tense",
    "semisextile": "minor", "semisquare": "minor", "quintile": "minor",
    "sesquiquadrate": "minor", "biquintile": "minor", "quincunx": "minor",
}

# QA-011: aspect names were ru/en-only, so es/pt/tr/uk showed English
# ("Conjunction", "Trine") in the natal chart, transits and compatibility
# synastry. Canonical astrological terms for the other four languages.
ASPECT_NAMES_I18N = {
    "es": {"conjunction": "Conjunción", "sextile": "Sextil", "square": "Cuadratura", "trine": "Trígono", "opposition": "Oposición",
           "semisextile": "Semisextil", "semisquare": "Semicuadratura", "quintile": "Quintil",
           "sesquiquadrate": "Sesquicuadratura", "biquintile": "Biquintil", "quincunx": "Quincuncio"},
    "pt": {"conjunction": "Conjunção", "sextile": "Sextil", "square": "Quadratura", "trine": "Trígono", "opposition": "Oposição",
           "semisextile": "Semissextil", "semisquare": "Semiquadratura", "quintile": "Quintil",
           "sesquiquadrate": "Sesquiquadratura", "biquintile": "Biquintil", "quincunx": "Quincôncio"},
    "tr": {"conjunction": "Kavuşum", "sextile": "Sekstil", "square": "Kare", "trine": "Üçgen", "opposition": "Karşıtlık",
           "semisextile": "Yarım sekstil", "semisquare": "Yarım kare", "quintile": "Kvintil",
           "sesquiquadrate": "Bir buçuk kare", "biquintile": "Bikvintil", "quincunx": "Kinkunks"},
    "uk": {"conjunction": "Сполучення", "sextile": "Секстиль", "square": "Квадрат", "trine": "Тригон", "opposition": "Опозиція",
           "semisextile": "Напівсекстиль", "semisquare": "Напівквадрат", "quintile": "Квінтиль",
           "sesquiquadrate": "Півтораквадрат", "biquintile": "Біквінтиль", "quincunx": "Квінконс"},
}


def _aspect_name(atype: str, name_ru: str, name_en: str, lang: str) -> str:
    if lang == "ru":
        return name_ru
    if lang == "en":
        return name_en
    return ASPECT_NAMES_I18N.get(lang, {}).get(atype, name_en)

HOUSE_NUM = {
    "First_House": 1, "Second_House": 2, "Third_House": 3, "Fourth_House": 4,
    "Fifth_House": 5, "Sixth_House": 6, "Seventh_House": 7, "Eighth_House": 8,
    "Ninth_House": 9, "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}

# TZ-103 step 0: kerykeion accepts 23 house-system identifiers natively via
# houses_system_identifier and already defaults to "P" — so Placidus was
# never something we had to implement, and switching systems is a parameter,
# not a calculation. These five are the ones the ticket asked for; the names
# are kerykeion's own (subject.houses_system_name) so ours can't drift from
# what the library actually applied.
HOUSE_SYSTEMS = {
    "P": "Placidus",
    "K": "Koch",
    "A": "Equal",
    "C": "Campanus",
    "R": "Regiomontanus",
}
DEFAULT_HOUSE_SYSTEM = "P"

# Optional chart points. "nodes" covers the lunar-node pair (North is read
# from kerykeion, South is its exact opposite), the rest are single bodies.
#
# lilith/chiron/nodes cost nothing: kerykeion computes all three on every
# subject we already build (disable_chiron_and_lilith defaults to False), we
# simply never read mean_lilith. The four asteroids aren't wrapped by
# kerykeion, but the ephemeris file that covers them ships inside the package
# — see _asteroid_point.
AVAILABLE_POINTS = ["nodes", "lilith", "chiron", "part_of_fortune",
                    "ceres", "pallas", "juno", "vesta"]
# What a request that doesn't say otherwise gets: everything the chart used to
# show, plus Lilith. Asteroids stay opt-in — they're the "if it's cheap" tier
# of the ticket, and nine extra glyphs would crowd the wheel by default.
DEFAULT_POINTS = ["nodes", "lilith", "chiron", "part_of_fortune"]

# Swiss Ephemeris body constants, resolved by name at call time rather than
# imported here: conftest.py stubs kerykeion out on Windows (pyswisseph has no
# wheel there), and a module-level `import swisseph` would break that stub and
# take the whole local test run down with it.
ASTEROID_IDS = {"ceres": "CERES", "pallas": "PALLAS", "juno": "JUNO", "vesta": "VESTA"}


def _ru(sign: str) -> str:
    return SIGNS_RU.get(sign, SIGNS_RU.get(sign[:3], sign))


def _normalize_sign(sign: str) -> str:
    for full in SIGN_ORDER:
        if sign.startswith(full[:3]):
            return full
    return sign


# TZ-080: planet/sign names were ru/en-only everywhere in this file. These
# resolve ES/PT/TR/UK via natal_i18n.py, falling back to English until a
# language is actually generated. Aspect names (ASPECT_TYPES) already have
# ru/en from TZ-076/079; the 5 long interpretation prompt templates are out
# of scope here (TZ-080 Module 5, handled separately).
def _planet_name(key: str, lang: str) -> str:
    if lang == "ru":
        return PLANET_NAMES_RU.get(key, key)
    en_value = PLANET_NAMES_EN.get(key, key.capitalize())
    if lang == "en":
        return en_value
    return localized_field(PLANET_NAMES_I18N, lang, key, "name", en_value)


def _sign_name(sign: str, lang: str) -> str:
    if lang == "ru":
        return _ru(sign)
    normalized = _normalize_sign(sign)
    if lang == "en":
        return normalized
    return localized_field(SIGNS_I18N, lang, normalized, "name", normalized)


def _sign_from_abs(abs_pos: float) -> str:
    return SIGN_ORDER[int(abs_pos / 30) % 12]


# QA-001/004: natal used to raise a raw "City not found: {city}" 422 while
# compatibility's partner form silently accepted the same bad input. Both now
# go through this one localized message instead of each inventing their own.
CITY_NOT_FOUND_MSGS = {
    "ru": "Город не найден, проверьте написание",
    "en": "City not found, check the spelling",
    "es": "Ciudad no encontrada, comprueba la ortografía",
    "pt": "Cidade não encontrada, verifique a ortografia",
    "tr": "Şehir bulunamadı, yazımı kontrol edin",
    "uk": "Місто не знайдено, перевірте написання",
}


async def geocode_city(city: str, lang: str = "ru") -> tuple[float, float]:
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "Mystral/1.0"},
        )
    data = resp.json()
    if not data:
        msg = CITY_NOT_FOUND_MSGS.get(lang, CITY_NOT_FOUND_MSGS["en"])
        raise HTTPException(status_code=422, detail=msg)
    return float(data[0]["lat"]), float(data[0]["lon"])


# Loads the tz-boundary dataset once; instantiating per-request is expensive.
_TZ_FINDER = TimezoneFinder()


def resolve_timezone(lat: float, lon: float) -> str:
    """IANA tz name for a coordinate, e.g. 'Europe/Moscow'.

    kerykeion localizes the given wall-clock birth time via pytz using this
    string (historical DST transitions included) before converting to UTC —
    passing "UTC" here (the old bug) skips that conversion entirely and
    treats local time as if it were already UTC.
    """
    return _TZ_FINDER.timezone_at(lat=lat, lng=lon) or "UTC"


def _build_subject(name: str, year: int, month: int, day: int,
                   hour: int, minute: int, lat: float, lon: float,
                   house_system: str = DEFAULT_HOUSE_SYSTEM) -> AstrologicalSubject:
    return AstrologicalSubject(
        name, year, month, day, hour, minute,
        lng=lon, lat=lat, tz_str=resolve_timezone(lat, lon), online=False,
        houses_system_identifier=house_system,
    )


def _get_abs_pos(p) -> float:
    abs_pos = getattr(p, "abs_pos", None)
    if abs_pos is not None:
        return float(abs_pos)
    sign = _normalize_sign(p.sign)
    idx = SIGN_ORDER.index(sign) if sign in SIGN_ORDER else 0
    return idx * 30 + p.position


def _extract_planet(subj: AstrologicalSubject, key: str, ptype: str = "planet", lang: str = "ru") -> dict | None:
    try:
        p = getattr(subj, key, None)
        if p is None or not hasattr(p, "sign"):
            return None
        sign_full = _normalize_sign(p.sign)
        house_raw = getattr(p, "house", None)
        house = HOUSE_NUM.get(house_raw, house_raw) if isinstance(house_raw, str) else house_raw
        return {
            "name": key,
            "name_ru": PLANET_NAMES_RU.get(key, key),
            "name_en": PLANET_NAMES_EN.get(key, key.capitalize()),
            "name_local": _planet_name(key, lang),
            "symbol": PLANET_SYMBOLS.get(key, "?"),
            "sign": sign_full,
            "sign_ru": _ru(p.sign),
            "sign_local": _sign_name(p.sign, lang),
            "degree": round(float(getattr(p, "position", 0)), 1),
            "abs_pos": round(_get_abs_pos(p), 1),
            "house": house,
            "retrograde": bool(getattr(p, "retrograde", False)),
            "type": ptype,
        }
    except Exception:
        return None


def _house_for(abs_pos: float, houses: list[dict]) -> int | None:
    """House number containing an ecliptic longitude, from the already-built
    cusp list. kerykeion tags the bodies it computes itself, but not the ones
    we read straight out of Swiss Ephemeris, so those get their house here —
    against the cusps of whichever house system the request asked for."""
    if len(houses) != 12:
        return None
    for h in houses:
        start = h["abs_pos"]
        end = houses[h["number"] % 12]["abs_pos"]
        inside = start <= abs_pos < end if end > start else (abs_pos >= start or abs_pos < end)
        if inside:
            return h["number"]
    return None


def _derived_point(key: str, abs_pos: float, lang: str, houses: list[dict],
                   ptype: str, retrograde: bool = False) -> dict:
    """Same dict shape as _extract_planet, for points we position ourselves
    rather than read off the kerykeion subject."""
    abs_pos = abs_pos % 360
    sign = _sign_from_abs(abs_pos)
    return {
        "name": key,
        "name_ru": PLANET_NAMES_RU.get(key, key),
        "name_en": PLANET_NAMES_EN.get(key, key.capitalize()),
        "name_local": _planet_name(key, lang),
        "symbol": PLANET_SYMBOLS.get(key, "?"),
        "sign": sign,
        "sign_ru": _ru(sign),
        "sign_local": _sign_name(sign, lang),
        "degree": round(abs_pos % 30, 1),
        "abs_pos": round(abs_pos, 1),
        "house": _house_for(abs_pos, houses),
        "retrograde": retrograde,
        "type": ptype,
    }


def _asteroid_point(subj: AstrologicalSubject, key: str, lang: str, houses: list[dict]) -> dict | None:
    """Ceres/Pallas/Juno/Vesta.

    kerykeion's Planet literal stops at Mean_Lilith, so these four aren't
    reachable through its API — but they are in the ephemeris it ships, and
    subj.julian_day is the instant it already resolved (birth time localized
    via pytz, then converted to UT). So this is still the library's own data
    and the library's own time, just fetched one level down instead of being
    recomputed here.

    Returns None rather than raising if the date falls outside the bundled
    asteroid file's 1800-2399 range — a missing asteroid is not a reason to
    fail the whole chart.
    """
    try:
        import kerykeion
        import swisseph as swe

        # kerykeion ships its own ephemeris directory (seas_18.se1 included)
        # and points swisseph at it when a subject is constructed. Setting it
        # explicitly instead of relying on that side effect keeps this correct
        # regardless of call order.
        swe.set_ephe_path(str(Path(kerykeion.__file__).parent / "sweph"))
        values, _flags = swe.calc_ut(subj.julian_day, getattr(swe, ASTEROID_IDS[key]),
                                     swe.FLG_SWIEPH | swe.FLG_SPEED)
        return _derived_point(key, values[0], lang, houses, "asteroid", retrograde=values[3] < 0)
    except Exception:
        return None


def _true_mc(subj: AstrologicalSubject) -> float | None:
    """Ecliptic longitude of the Midheaven.

    Not the same thing as the 10th house cusp: they coincide in the quadrant
    systems (Placidus, Koch, Campanus, Regiomontanus) but not in Equal, where
    cusp 10 is simply Ascendant + 270°. Swiss Ephemeris returns the real MC in
    its ascmc array for any house system, so the axis label stays correct
    whichever one the user picked.
    """
    try:
        import swisseph as swe

        _cusps, ascmc = swe.houses_ex(subj.julian_day, subj.lat, subj.lng, b"P")
        return float(ascmc[1])
    except Exception:
        return None


def _calc_aspects(planets: list[dict], lang: str = "ru", include_minor: bool = True) -> list[dict]:
    table = ALL_ASPECT_TYPES if include_minor else ASPECT_TYPES
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            diff = abs(p1["abs_pos"] - p2["abs_pos"])
            if diff > 180:
                diff = 360 - diff
            for angle, max_orb, atype, name_ru, name_en, symbol in table:
                orb = abs(diff - angle)
                if orb <= max_orb:
                    category = ASPECT_CATEGORY[atype]
                    aspects.append({
                        "planet1": p1["name"], "planet1_ru": p1["name_ru"], "planet1_en": p1.get("name_en", p1["name"]),
                        "planet1_local": p1.get("name_local", p1["name"]),
                        "planet2": p2["name"], "planet2_ru": p2["name_ru"], "planet2_en": p2.get("name_en", p2["name"]),
                        "planet2_local": p2.get("name_local", p2["name"]),
                        "type": atype, "name_ru": name_ru, "name_en": name_en,
                        "name_local": _aspect_name(atype, name_ru, name_en, lang), "symbol": symbol,
                        "orb": round(orb, 1), "harmony": atype in ("trine", "sextile"),
                        "category": category, "is_major": category != "minor",
                    })
                    break
    aspects.sort(key=lambda a: a["orb"])
    return aspects


def build_full_chart(subj: AstrologicalSubject, lang: str = "ru",
                     points: list[str] | None = None) -> dict:
    selected = list(points) if points is not None else list(DEFAULT_POINTS)
    planet_keys = ["sun", "moon", "mercury", "venus", "mars",
                   "jupiter", "saturn", "uranus", "neptune", "pluto"]
    planets = [p for p in (_extract_planet(subj, k, lang=lang) for k in planet_keys) if p is not None]

    # Houses first: the optional points below are placed against these cusps,
    # so they follow whichever house system the request selected.
    house_attrs = ["first_house", "second_house", "third_house", "fourth_house",
                   "fifth_house", "sixth_house", "seventh_house", "eighth_house",
                   "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"]
    houses = []
    for i, attr in enumerate(house_attrs, 1):
        try:
            h = getattr(subj, attr)
            houses.append({
                "number": i, "sign": _normalize_sign(h.sign),
                "sign_ru": _ru(h.sign), "sign_local": _sign_name(h.sign, lang),
                "degree": round(float(getattr(h, "position", 0)), 1),
                "abs_pos": round(_get_abs_pos(h), 1),
            })
        except Exception:
            houses.append({"number": i, "sign": "Aries", "sign_ru": "Овен",
                           "sign_local": _sign_name("Aries", lang), "degree": 0, "abs_pos": (i - 1) * 30})

    extra = []
    if "nodes" in selected:
        node = _extract_planet(subj, "true_node", "node", lang=lang)
        if node is None:
            for attr in ["mean_node", "north_node"]:
                node = _extract_planet(subj, attr, "node", lang=lang)
                if node:
                    node["name"] = "true_node"
                    node["name_ru"] = "Сев. узел"
                    node["name_local"] = _planet_name("true_node", lang)
                    node["symbol"] = "☊"
                    break
        if node:
            extra.append(node)
            extra.append(_derived_point("south_node", node["abs_pos"] + 180, lang, houses, "node"))

    if "lilith" in selected:
        # kerykeion calls it mean_lilith; it's the mean Black Moon, the variant
        # every mainstream calculator shows by default.
        lilith = _extract_planet(subj, "mean_lilith", "point", lang=lang)
        if lilith:
            lilith["name"] = "lilith"
            lilith["name_ru"] = PLANET_NAMES_RU["lilith"]
            lilith["name_en"] = PLANET_NAMES_EN["lilith"]
            lilith["name_local"] = _planet_name("lilith", lang)
            lilith["symbol"] = PLANET_SYMBOLS["lilith"]
            extra.append(lilith)

    if "chiron" in selected:
        chiron = _extract_planet(subj, "chiron", "asteroid", lang=lang)
        if chiron:
            extra.append(chiron)

    for key in ("ceres", "pallas", "juno", "vesta"):
        if key in selected:
            asteroid = _asteroid_point(subj, key, lang, houses)
            if asteroid:
                extra.append(asteroid)

    # Part of Fortune: ASC + Moon - Sun (mod 360)
    part_of_fortune = None
    if "part_of_fortune" in selected:
        try:
            if len(planets) >= 2:
                pof_abs = (_get_abs_pos(subj.first_house) + planets[1]["abs_pos"] - planets[0]["abs_pos"]) % 360
                part_of_fortune = _derived_point("part_of_fortune", pof_abs, lang, houses, "point")
        except Exception:
            pass

    # TZ-103: the aspect grid now spans the optional points too — a Chiron
    # square or a Lilith conjunction is exactly the kind of thing someone
    # enables those points to see. The South Node is left out on purpose: it
    # sits 180° from the North Node by construction, so every one of its
    # aspects is the mirror of a North Node aspect already in the list.
    aspect_bodies = planets + [p for p in extra if p["name"] != "south_node"]
    aspects = _calc_aspects(aspect_bodies, lang)
    all_planets = planets + extra

    # Element/modality balance
    el = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    mod = {"cardinal": 0, "fixed": 0, "mutable": 0}
    sign_count: dict[str, int] = {}
    for p in planets:
        e = ELEMENTS.get(p["sign"], "")
        m = MODALITIES.get(p["sign"], "")
        if e: el[e] += 1
        if m: mod[m] += 1
        sign_count[p["sign"]] = sign_count.get(p["sign"], 0) + 1

    # Stelliums (3+ planets in same sign or house)
    stelliums = []
    for s, ps in sign_count.items():
        if ps >= 3:
            names_ru = [p["name_ru"] for p in planets if p["sign"] == s]
            names_en = [p.get("name_en", p["name"]) for p in planets if p["sign"] == s]
            names_local = [p.get("name_local", p["name"]) for p in planets if p["sign"] == s]
            stelliums.append({"type": "sign", "name_ru": _ru(s), "name_en": s, "name_local": _sign_name(s, lang),
                              "planets_ru": names_ru, "planets_en": names_en, "planets_local": names_local})
    house_groups_ru: dict[int, list[str]] = {}
    house_groups_en: dict[int, list[str]] = {}
    house_groups_local: dict[int, list[str]] = {}
    for p in planets:
        if p["house"]:
            house_groups_ru.setdefault(p["house"], []).append(p["name_ru"])
            house_groups_en.setdefault(p["house"], []).append(p.get("name_en", p["name"]))
            house_groups_local.setdefault(p["house"], []).append(p.get("name_local", p["name"]))
    for h in house_groups_ru:
        if len(house_groups_ru[h]) >= 3:
            stelliums.append({"type": "house", "name_ru": f"Дом {h}", "name_en": f"House {h}", "name_local": f"House {h}",
                              "planets_ru": house_groups_ru[h], "planets_en": house_groups_en[h],
                              "planets_local": house_groups_local[h]})

    dominant_sign = max(sign_count, key=sign_count.get) if sign_count else ""

    # abs_pos on the two angles is what lets the wheel rotate itself so the
    # Ascendant sits on the left horizon (TZ-103 step 0) instead of pinning
    # 0° Aries there.
    try:
        asc = {"sign": _normalize_sign(subj.first_house.sign),
               "sign_ru": _ru(subj.first_house.sign), "sign_local": _sign_name(subj.first_house.sign, lang),
               "degree": round(float(subj.first_house.position), 1),
               "abs_pos": round(_get_abs_pos(subj.first_house), 1)}
    except Exception:
        asc = houses[0] if houses else {"sign": "Aries", "sign_ru": "Овен",
                                         "sign_local": _sign_name("Aries", lang), "degree": 0, "abs_pos": 0}

    try:
        mc_abs = _true_mc(subj)
        if mc_abs is None:
            mc_abs = _get_abs_pos(subj.tenth_house)
        mc_sign = _sign_from_abs(mc_abs)
        mc = {"sign": mc_sign, "sign_ru": _ru(mc_sign), "sign_local": _sign_name(mc_sign, lang),
              "degree": round(mc_abs % 30, 1), "abs_pos": round(mc_abs, 1)}
    except Exception:
        mc = houses[9] if len(houses) > 9 else {"sign": "Aries", "sign_ru": "Овен",
                                                  "sign_local": _sign_name("Aries", lang), "degree": 0, "abs_pos": 270}

    return {
        "planets": planets,
        "extra_points": extra,
        "houses": houses,
        "aspects": aspects,
        "ascendant": asc,
        "midheaven": mc,
        "part_of_fortune": part_of_fortune,
        "stelliums": stelliums,
        "element_balance": el,
        "modality_balance": mod,
        "dominant_sign": dominant_sign,
        "dominant_sign_ru": _ru(dominant_sign) if dominant_sign else "",
        "dominant_sign_local": _sign_name(dominant_sign, lang) if dominant_sign else "",
        # Echoed back from the subject rather than from the request, so what
        # the client displays is what the library actually applied.
        "house_system": {
            "code": getattr(subj, "houses_system_identifier", DEFAULT_HOUSE_SYSTEM),
            "name": getattr(subj, "houses_system_name", HOUSE_SYSTEMS[DEFAULT_HOUSE_SYSTEM]),
        },
        "points_included": [k for k in AVAILABLE_POINTS if k in selected],
    }


class NatalRequest(BaseModel):
    # QA-029/030: a direct POST bypassing the frontend's own validation used
    # to reach kerykeion with e.g. month=13/day=32 (raw 500) or a 5000-char
    # name (silently accepted, HTTP 200). Field bounds below turn those into
    # a clean 422 before any calculation is attempted.
    name: str = Field(min_length=1, max_length=100)
    year: int
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    # QA-002: None (not 12/0) means "birth time not provided" — distinct from
    # an explicit midnight/noon entry, so the endpoint can flag the result as
    # approximate instead of silently substituting a default.
    hour: Optional[int] = Field(default=None, ge=0, le=23)
    minute: Optional[int] = Field(default=None, ge=0, le=59)
    city: str
    lang: str = "ru"
    # TZ-103. Both default to the previous behaviour, so a client that
    # doesn't know about these fields gets the same chart it always got —
    # except for Lilith, which joins the default point set.
    house_system: str = DEFAULT_HOUSE_SYSTEM
    points: Optional[list[str]] = None

    @model_validator(mode="after")
    def _validate_calendar_date(self):
        try:
            date_cls(self.year, self.month, self.day)
        except ValueError as e:
            raise ValueError(f"Invalid calendar date: {e}")
        return self

    @model_validator(mode="after")
    def _validate_chart_options(self):
        if self.house_system not in HOUSE_SYSTEMS:
            raise ValueError(f"Unknown house system: {self.house_system}")
        if self.points is not None:
            unknown = [p for p in self.points if p not in AVAILABLE_POINTS]
            if unknown:
                raise ValueError(f"Unknown chart points: {', '.join(unknown)}")
        return self


class InterpretRequest(NatalRequest):
    section: str = "personality"


DEFAULT_BIRTH_HOUR = 12
DEFAULT_BIRTH_MINUTE = 0


def _resolve_birth_time(req: NatalRequest) -> tuple[int, int, bool]:
    """Returns (hour, minute, time_known) — substituting the documented
    default only when the client left birth time unset."""
    time_known = req.hour is not None
    hour = req.hour if time_known else DEFAULT_BIRTH_HOUR
    minute = req.minute if req.minute is not None else DEFAULT_BIRTH_MINUTE
    return hour, minute, time_known


@router.post("/natal/calculate")
async def natal_calculate(req: NatalRequest, current_user: User = Depends(get_current_user)):
    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "natal_calculate", 10, 10, window=60)
    lat, lon = await geocode_city(req.city, req.lang)
    hour, minute, time_known = _resolve_birth_time(req)
    try:
        subj = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon,
                              house_system=req.house_system)
        chart = build_full_chart(subj, lang=req.lang, points=req.points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")
    chart["time_known"] = time_known
    chart["time_used"] = f"{hour:02d}:{minute:02d}"
    return chart


@router.get("/natal/options")
async def natal_options(current_user: User = Depends(get_current_user)):
    """House systems and optional points the backend will accept, so the form
    doesn't hardcode a list that can drift from what kerykeion supports."""
    return {
        "house_systems": [{"code": c, "name": n} for c, n in HOUSE_SYSTEMS.items()],
        "default_house_system": DEFAULT_HOUSE_SYSTEM,
        "points": AVAILABLE_POINTS,
        "default_points": DEFAULT_POINTS,
    }


@router.post("/natal/svg")
async def natal_svg(req: NatalRequest, current_user: User = Depends(get_current_user)):
    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "natal_svg", 10, 10, window=60)
    lat, lon = await geocode_city(req.city, req.lang)
    hour, minute, _ = _resolve_birth_time(req)
    try:
        from kerykeion import KerykeionChartSVG
        subj = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon,
                              house_system=req.house_system)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, dir="/tmp") as tmp:
            tmp_path = tmp.name
        chart_svg = KerykeionChartSVG(subj, new_output_directory="/tmp")
        chart_svg.makeSVG()
        # kerykeion 4.x writes "<name> - Natal Chart.svg"; the old "<name>NatalChart.svg"
        # never matched, so this endpoint silently fell through to the empty
        # NamedTemporaryFile and returned a zero-byte SVG. Nothing in the app
        # calls it, which is why it went unnoticed.
        svg_path = os.path.join("/tmp", f"{req.name} - Natal Chart.svg")
        if not os.path.exists(svg_path):
            svg_path = tmp_path
        with open(svg_path, "r") as f:
            svg_content = f.read()
        try:
            os.unlink(svg_path)
            os.unlink(tmp_path)
        except OSError:
            pass
        return Response(content=svg_content, media_type="image/svg+xml")
    except ImportError:
        raise HTTPException(501, "KerykeionChartSVG not available")
    except Exception as e:
        raise HTTPException(500, f"SVG generation failed: {e}")


@router.post("/natal/transits")
async def natal_transits(req: NatalRequest, current_user: User = Depends(get_current_user)):
    lat, lon = await geocode_city(req.city, req.lang)
    hour, minute, _ = _resolve_birth_time(req)
    natal = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon)
    now = datetime.utcnow()
    transit = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)

    ru = req.lang == "ru"
    pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    natal_planets = [_extract_planet(natal, k, lang=req.lang) for k in pkeys]
    transit_planets = [_extract_planet(transit, k, lang=req.lang) for k in pkeys]

    active = []
    for tp in transit_planets:
        for np in natal_planets:
            diff = abs(tp["abs_pos"] - np["abs_pos"])
            if diff > 180: diff = 360 - diff
            for angle, _, atype, name_ru, name_en, symbol in ASPECT_TYPES:
                orb = abs(diff - angle)
                if orb <= 3:
                    active.append({
                        "transit_planet": tp["name_local"], "transit_sign": tp["sign_local"],
                        "natal_planet": np["name_local"], "natal_sign": np["sign_local"],
                        "aspect": _aspect_name(atype, name_ru, name_en, req.lang), "aspect_symbol": symbol, "orb": round(orb, 1),
                    })
                    break
    active.sort(key=lambda a: a["orb"])
    return {"transits": active[:5], "date": now.isoformat()}


SECTION_PROMPTS_RU = {
    "personality": (
        "Дай интерпретацию натальной карты.\n"
        "Проанализируй Солнце в {sun}, Луну в {moon}, Асцендент в {asc} как единую систему.\n"
        "Как эти три энергии взаимодействуют? Где конфликт, где гармония?\n"
        "Интерпретируй через призму психологии и реальной жизни, называя конкретные планеты и знаки "
        "из карты пользователя — не абстрактные описания знаков, а разбор реальных позиций.\n"
        "150-250 слов, без воды."
    ),
    "planets": (
        "Дай интерпретацию натальной карты.\n"
        "Планеты: {planets_text}.\nДополнительные точки: {extra_text}.\n"
        "Какая планета самая сильная и почему? Ретроградные — на что обратить внимание?\n"
        "Обязательно разбери и дополнительные точки, а не только десять планет: "
        "лунные узлы — направление роста и то, что уже отработано; Лилит — теневая, "
        "вытесненная часть; Хирон — рана и то, в чём человек становится целителем "
        "для других; астероиды, если они есть в списке.\n"
        "Называй конкретные планеты, знаки и градусы из карты пользователя, не абстрактные описания.\n"
        "150-250 слов, без воды."
    ),
    "houses": (
        "Дай интерпретацию натальной карты.\n"
        "Система домов: {house_system}.\nДома: {houses_text}.\nСтеллиумы: {stellium_text}.\n"
        "Какие дома наполнены? Где акцент жизни? Пустые дома — что значит?\n"
        "Интерпретируй через призму реальной жизни, называя конкретные дома и планеты из карты пользователя.\n"
        "150-250 слов, без воды."
    ),
    "aspects": (
        "Дай интерпретацию натальной карты.\n"
        "Мажорные аспекты: {aspects_text}.\nМинорные аспекты: {minor_aspects_text}.\n"
        "Объясни влияние каждого на жизнь конкретно. Какой аспект самый мощный?\n"
        "Мажорные — основной каркас характера. Минорные бери как оттенки и нюансы, "
        "не раздувай их до уровня мажорных: у них орбис около градуса, они уточняют "
        "картину, а не задают её.\n"
        "Называй конкретные планеты и аспекты из карты пользователя, не абстрактные описания.\n"
        "150-250 слов, без воды."
    ),
    "transits": (
        "Дай интерпретацию натальной карты.\n"
        "Активные транзиты на сегодня: {transits_text}.\n"
        "Обозначения: T: — транзитная планета, N: — натальная.\n"
        "Что это значит прямо сейчас? Практический совет.\n"
        "Называй конкретные планеты и аспекты из карты пользователя.\n"
        "150-250 слов, без воды."
    ),
}
SECTION_PROMPTS_EN = {
    "personality": (
        "Give an interpretation of the natal chart.\n"
        "Analyze Sun in {sun}, Moon in {moon}, Ascendant in {asc} as a unified system.\n"
        "How do these three energies interact? Where's conflict, where's harmony?\n"
        "Interpret through the lens of psychology and real life, naming specific planets and signs "
        "from the user's own chart — not abstract sign descriptions, but the actual positions.\n"
        "150-250 words, no filler."
    ),
    "planets": (
        "Give an interpretation of the natal chart.\n"
        "Planets: {planets_text}.\nAdditional points: {extra_text}.\n"
        "Which planet is strongest and why? Retrograde — what to watch for?\n"
        "Cover the additional points too, not just the ten planets: the lunar nodes "
        "as direction of growth and what's already been worked through; Lilith as the "
        "shadow, disowned part; Chiron as the wound the person ends up healing in "
        "others; and any asteroids present in the list.\n"
        "Name specific planets, signs and degrees from the user's chart, not abstract descriptions.\n"
        "150-250 words, no filler."
    ),
    "houses": (
        "Give an interpretation of the natal chart.\n"
        "House system: {house_system}.\nHouses: {houses_text}.\nStelliums: {stellium_text}.\n"
        "Which houses are packed? Life focus? Empty houses — meaning?\n"
        "Interpret through the lens of real life, naming specific houses and planets from the chart.\n"
        "150-250 words, no filler."
    ),
    "aspects": (
        "Give an interpretation of the natal chart.\n"
        "Major aspects: {aspects_text}.\nMinor aspects: {minor_aspects_text}.\n"
        "Explain each aspect's impact on life specifically. Which is most powerful?\n"
        "The majors are the structural frame of the character. Treat the minors as "
        "shading and nuance — don't inflate them to major status: their orb is about "
        "a degree, they refine the picture rather than set it.\n"
        "Name specific planets and aspects from the user's chart, not abstract descriptions.\n"
        "150-250 words, no filler."
    ),
    "transits": (
        "Give an interpretation of the natal chart.\n"
        "Active transits today: {transits_text}.\n"
        "Notation: T: = transiting planet, N: = natal planet.\n"
        "What does this mean right now? Practical advice.\n"
        "Name specific planets and aspects from the user's chart.\n"
        "150-250 words, no filler."
    ),
}


@router.post("/natal/interpret")
async def natal_interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # get_current_user pulls a pooled connection via its own Depends(get_session);
    # release it now instead of holding it for the whole SSE stream below.
    await session.close()
    if req.section != "personality" and current_user.subscription_tier == "free":
        raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    if current_user.subscription_tier == "free":
        key = f"natal_count:{current_user.id}"
        count = await redis_client.incr(key)
        if count > 3:
            raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    try:
        lat, lon = await geocode_city(req.city, req.lang)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Geocoding failed: {e}")

    hour, minute, _ = _resolve_birth_time(req)
    try:
        subj = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon,
                              house_system=req.house_system)
        chart = build_full_chart(subj, lang=req.lang, points=req.points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")

    templates = SECTION_PROMPTS_RU if req.lang == "ru" else SECTION_PROMPTS_EN
    template = templates.get(req.section, templates["personality"])

    # TZ-103: the chart facts fed to the model used to be assembled from the
    # _ru fields with Russian connectors ("в", "Дом", "нет") hardcoded, so an
    # ES/PT/TR/UK user's prompt described their chart in Russian and only
    # lang_enforce() pulled the answer back into their language. The
    # *_local fields already carry every language (TZ-080), so use those and
    # keep the separators symbolic instead of translating glue words.
    p = chart.get("planets", [])
    sun_s = p[0]["sign_local"] if len(p) > 0 else "?"
    moon_s = p[1]["sign_local"] if len(p) > 1 else "?"
    asc_s = chart.get("ascendant", {}).get("sign_local", "?")
    none_word = "нет" if req.lang == "ru" else "none"
    planets_text = ", ".join(
        f"{pl['name_local']} — {pl['sign_local']} {pl['degree']}°{' R' if pl['retrograde'] else ''}"
        + (f" (H{pl['house']})" if pl["house"] else "")
        for pl in chart["planets"])
    extra_text = ", ".join(
        f"{ep['name_local']} — {ep['sign_local']} {ep['degree']}°{' R' if ep['retrograde'] else ''}"
        for ep in chart.get("extra_points", [])) or none_word
    houses_text = ", ".join(f"H{h['number']}: {h['sign_local']} {h['degree']}°" for h in chart["houses"])

    def _aspect_line(a: dict) -> str:
        return f"{a['planet1_local']} {a['symbol']} {a['planet2_local']} {a['name_local']} ({a['orb']}°)"

    # Aspects arrive sorted by orb, so the head of each list is the tightest.
    all_aspects = chart.get("aspects", [])
    majors = [a for a in all_aspects if a.get("is_major", True)]
    minors = [a for a in all_aspects if not a.get("is_major", True)]
    aspects_text = ", ".join(_aspect_line(a) for a in majors[:6]) or none_word
    minor_aspects_text = ", ".join(_aspect_line(a) for a in minors[:4]) or none_word
    # stelliums store planets_ru/_en/_local — the old code read a "planets"
    # key that has never existed, so every stellium reached the model as a
    # bare sign name with an empty planet list.
    stellium_text = "; ".join(
        f"{s.get('name_local') or s.get('name_en', '?')}: {', '.join(s.get('planets_local', []))}"
        for s in chart.get("stelliums", [])) or none_word
    house_system_text = chart.get("house_system", {}).get("name", HOUSE_SYSTEMS[DEFAULT_HOUSE_SYSTEM])

    transits_text = ""
    if req.section == "transits":
        now = datetime.utcnow()
        t_subj = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)
        pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
        actives = []
        for k in pkeys:
            tp = _extract_planet(t_subj, k, lang=req.lang)
            for np_item in chart["planets"]:
                diff = abs(tp["abs_pos"] - np_item["abs_pos"])
                if diff > 180: diff = 360 - diff
                for angle, _, atype, name_ru, name_en, sym in ASPECT_TYPES:
                    if abs(diff - angle) <= 3:
                        # T:/N: rather than the old "Транзит ... натал. ..."
                        # wording — the prefixes carry the same distinction
                        # without hardcoding Russian into every language, and
                        # the template explains the notation.
                        actives.append(
                            f"T:{tp['name_local']} {sym} N:{np_item['name_local']} "
                            f"{_aspect_name(atype, name_ru, name_en, req.lang)} ({round(abs(diff - angle), 1)}°)")
                        break
        transits_text = "; ".join(actives[:5]) or none_word

    prompt = template.format(sun=sun_s, moon=moon_s, asc=asc_s, planets_text=planets_text,
                             extra_text=extra_text, houses_text=houses_text,
                             aspects_text=aspects_text,
                             minor_aspects_text=minor_aspects_text,
                             house_system=house_system_text,
                             transits_text=transits_text, stellium_text=stellium_text)
    prompt += lang_enforce(req.lang)

    # TZ-103 grew the "planets" and "aspects" prompts: the model is now
    # explicitly told to also cover the optional points (up to 8, versus the
    # 3 that were always unconditionally present before) and both major AND
    # minor aspects (up to 10 lines, versus 5 major-only before). Same class
    # of risk QA-015/016 found in horoscope.py — the requested word count
    # ("150-250 слов") didn't grow, but real generations tend to run long
    # when asked to name more entities, and a max_tokens ceiling sized for
    # the old content volume can then cut a longer one off mid-sentence.
    # Scaled the same way tarot.py already scales with card count, rather
    # than raising every section's ceiling regardless of whether its content
    # actually grew (personality/houses/transits didn't).
    extra_count = len(chart.get("extra_points", []))
    has_minors = any(not a.get("is_major", True) for a in all_aspects)
    if req.section == "aspects":
        max_tokens = 1800 if has_minors else 1400
    elif req.section == "planets":
        max_tokens = 1800 if extra_count > 4 else 1400
    else:
        max_tokens = 1400

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "natal_interpret", 2, 20)
    sys = system_prompt(req.lang) + lang_enforce(req.lang)
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=max_tokens, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
