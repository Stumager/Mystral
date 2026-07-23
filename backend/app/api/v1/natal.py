import json
import os
import tempfile
from datetime import date as date_cls, datetime
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

PLANET_SYMBOLS = {
    "sun": "☀️", "moon": "🌙", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇",
    "true_node": "☊", "chiron": "⚷",
}
PLANET_NAMES_RU = {
    "sun": "Солнце", "moon": "Луна", "mercury": "Меркурий", "venus": "Венера",
    "mars": "Марс", "jupiter": "Юпитер", "saturn": "Сатурн",
    "uranus": "Уран", "neptune": "Нептун", "pluto": "Плутон",
    "true_node": "Сев. узел", "south_node": "Юж. узел", "chiron": "Хирон",
}
PLANET_NAMES_EN = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus",
    "mars": "Mars", "jupiter": "Jupiter", "saturn": "Saturn",
    "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto",
    "true_node": "North Node", "south_node": "South Node", "chiron": "Chiron",
}

ASPECT_TYPES = [
    (0, 8, "conjunction", "Соединение", "Conjunction", "☌"),
    (60, 6, "sextile", "Секстиль", "Sextile", "⚹"),
    (90, 8, "square", "Квадрат", "Square", "□"),
    (120, 8, "trine", "Трин", "Trine", "△"),
    (180, 8, "opposition", "Оппозиция", "Opposition", "☍"),
]

# QA-011: aspect names were ru/en-only, so es/pt/tr/uk showed English
# ("Conjunction", "Trine") in the natal chart, transits and compatibility
# synastry. Canonical astrological terms for the other four languages.
ASPECT_NAMES_I18N = {
    "es": {"conjunction": "Conjunción", "sextile": "Sextil", "square": "Cuadratura", "trine": "Trígono", "opposition": "Oposición"},
    "pt": {"conjunction": "Conjunção", "sextile": "Sextil", "square": "Quadratura", "trine": "Trígono", "opposition": "Oposição"},
    "tr": {"conjunction": "Kavuşum", "sextile": "Sekstil", "square": "Kare", "trine": "Üçgen", "opposition": "Karşıtlık"},
    "uk": {"conjunction": "Сполучення", "sextile": "Секстиль", "square": "Квадрат", "trine": "Тригон", "opposition": "Опозиція"},
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
                   hour: int, minute: int, lat: float, lon: float) -> AstrologicalSubject:
    return AstrologicalSubject(
        name, year, month, day, hour, minute,
        lng=lon, lat=lat, tz_str=resolve_timezone(lat, lon), online=False,
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


def _calc_aspects(planets: list[dict], lang: str = "ru") -> list[dict]:
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            diff = abs(p1["abs_pos"] - p2["abs_pos"])
            if diff > 180:
                diff = 360 - diff
            for angle, max_orb, atype, name_ru, name_en, symbol in ASPECT_TYPES:
                orb = abs(diff - angle)
                if orb <= max_orb:
                    aspects.append({
                        "planet1": p1["name"], "planet1_ru": p1["name_ru"], "planet1_en": p1.get("name_en", p1["name"]),
                        "planet1_local": p1.get("name_local", p1["name"]),
                        "planet2": p2["name"], "planet2_ru": p2["name_ru"], "planet2_en": p2.get("name_en", p2["name"]),
                        "planet2_local": p2.get("name_local", p2["name"]),
                        "type": atype, "name_ru": name_ru, "name_en": name_en,
                        "name_local": _aspect_name(atype, name_ru, name_en, lang), "symbol": symbol,
                        "orb": round(orb, 1), "harmony": atype in ("trine", "sextile"),
                    })
                    break
    aspects.sort(key=lambda a: a["orb"])
    return aspects


def build_full_chart(subj: AstrologicalSubject, lang: str = "ru") -> dict:
    planet_keys = ["sun", "moon", "mercury", "venus", "mars",
                   "jupiter", "saturn", "uranus", "neptune", "pluto"]
    planets = [p for p in (_extract_planet(subj, k, lang=lang) for k in planet_keys) if p is not None]

    # Extra points: True Node, Chiron
    extra = []
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
        south_abs = (node["abs_pos"] + 180) % 360
        south_sign = _sign_from_abs(south_abs)
        extra.append({
            "name": "south_node", "name_ru": "Юж. узел", "name_en": "South Node",
            "name_local": _planet_name("south_node", lang), "symbol": "☋",
            "sign": south_sign, "sign_ru": _ru(south_sign), "sign_local": _sign_name(south_sign, lang),
            "degree": round(south_abs % 30, 1), "abs_pos": round(south_abs, 1),
            "house": None, "retrograde": False, "type": "node",
        })

    chiron = _extract_planet(subj, "chiron", "asteroid", lang=lang)
    if chiron:
        extra.append(chiron)

    all_planets = planets + extra
    aspects = _calc_aspects(planets, lang)

    # Houses
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

    # Part of Fortune: ASC + Moon - Sun (mod 360)
    part_of_fortune = None
    try:
        if len(planets) >= 2:
            asc_abs = _get_abs_pos(subj.first_house)
            moon_abs = planets[1]["abs_pos"]
            sun_abs = planets[0]["abs_pos"]
            pof_abs = (asc_abs + moon_abs - sun_abs) % 360
            pof_sign = _sign_from_abs(pof_abs)
            part_of_fortune = {
                "sign": pof_sign, "sign_ru": _ru(pof_sign), "sign_local": _sign_name(pof_sign, lang),
                "degree": round(pof_abs % 30, 1), "house": None,
            }
    except Exception:
        pass

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

    try:
        asc = {"sign": _normalize_sign(subj.first_house.sign),
               "sign_ru": _ru(subj.first_house.sign), "sign_local": _sign_name(subj.first_house.sign, lang),
               "degree": round(float(subj.first_house.position), 1)}
    except Exception:
        asc = houses[0] if houses else {"sign": "Aries", "sign_ru": "Овен",
                                         "sign_local": _sign_name("Aries", lang), "degree": 0}

    try:
        mc = {"sign": _normalize_sign(subj.tenth_house.sign),
              "sign_ru": _ru(subj.tenth_house.sign), "sign_local": _sign_name(subj.tenth_house.sign, lang),
              "degree": round(float(subj.tenth_house.position), 1)}
    except Exception:
        mc = houses[9] if len(houses) > 9 else {"sign": "Aries", "sign_ru": "Овен",
                                                  "sign_local": _sign_name("Aries", lang), "degree": 0}

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

    @model_validator(mode="after")
    def _validate_calendar_date(self):
        try:
            date_cls(self.year, self.month, self.day)
        except ValueError as e:
            raise ValueError(f"Invalid calendar date: {e}")
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
        subj = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon)
        chart = build_full_chart(subj, lang=req.lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")
    chart["time_known"] = time_known
    chart["time_used"] = f"{hour:02d}:{minute:02d}"
    return chart


@router.post("/natal/svg")
async def natal_svg(req: NatalRequest, current_user: User = Depends(get_current_user)):
    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "natal_svg", 10, 10, window=60)
    lat, lon = await geocode_city(req.city, req.lang)
    hour, minute, _ = _resolve_birth_time(req)
    try:
        from kerykeion import KerykeionChartSVG
        subj = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, dir="/tmp") as tmp:
            tmp_path = tmp.name
        chart_svg = KerykeionChartSVG(subj, new_output_directory="/tmp")
        chart_svg.makeSVG()
        svg_path = os.path.join("/tmp", f"{req.name}NatalChart.svg")
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
        "Планеты: {planets_text}.\nДополнительно: {extra_text}.\n"
        "Какая планета самая сильная и почему? Ретроградные — на что обратить внимание?\n"
        "Называй конкретные планеты, знаки и градусы из карты пользователя, не абстрактные описания.\n"
        "150-250 слов, без воды."
    ),
    "houses": (
        "Дай интерпретацию натальной карты.\n"
        "Дома: {houses_text}.\nСтеллиумы: {stellium_text}.\n"
        "Какие дома наполнены? Где акцент жизни? Пустые дома — что значит?\n"
        "Интерпретируй через призму реальной жизни, называя конкретные дома и планеты из карты пользователя.\n"
        "150-250 слов, без воды."
    ),
    "aspects": (
        "Дай интерпретацию натальной карты.\n"
        "Топ аспекты: {aspects_text}.\n"
        "Объясни влияние каждого на жизнь конкретно. Какой аспект самый мощный?\n"
        "Называй конкретные планеты и аспекты из карты пользователя, не абстрактные описания.\n"
        "150-250 слов, без воды."
    ),
    "transits": (
        "Дай интерпретацию натальной карты.\n"
        "Активные транзиты на сегодня: {transits_text}.\n"
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
        "Planets: {planets_text}.\nExtra: {extra_text}.\n"
        "Which planet is strongest and why? Retrograde — what to watch for?\n"
        "Name specific planets, signs and degrees from the user's chart, not abstract descriptions.\n"
        "150-250 words, no filler."
    ),
    "houses": (
        "Give an interpretation of the natal chart.\n"
        "Houses: {houses_text}.\nStelliums: {stellium_text}.\n"
        "Which houses are packed? Life focus? Empty houses — meaning?\n"
        "Interpret through the lens of real life, naming specific houses and planets from the chart.\n"
        "150-250 words, no filler."
    ),
    "aspects": (
        "Give an interpretation of the natal chart.\n"
        "Top aspects: {aspects_text}.\n"
        "Explain each aspect's impact on life specifically. Which is most powerful?\n"
        "Name specific planets and aspects from the user's chart, not abstract descriptions.\n"
        "150-250 words, no filler."
    ),
    "transits": (
        "Give an interpretation of the natal chart.\n"
        "Active transits today: {transits_text}.\n"
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
        subj = _build_subject(req.name, req.year, req.month, req.day, hour, minute, lat, lon)
        # lang is threaded through purely so the chart's planet/sign fields are
        # internally consistent; the prompt templates below are still ru/en-only
        # (TZ-080 Module 5, handled separately) and don't read the new fields.
        chart = build_full_chart(subj, lang=req.lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")

    templates = SECTION_PROMPTS_RU if req.lang == "ru" else SECTION_PROMPTS_EN
    template = templates.get(req.section, templates["personality"])

    sru = req.lang == "ru"
    p = chart.get("planets", [])
    sun_s = p[0]["sign_ru" if sru else "sign"] if len(p) > 0 else "?"
    moon_s = p[1]["sign_ru" if sru else "sign"] if len(p) > 1 else "?"
    asc_s = chart.get("ascendant", {}).get("sign_ru" if sru else "sign", "?")
    planets_text = ", ".join(f"{pl['name_ru' if sru else 'name']} в {pl['sign_ru' if sru else 'sign']}{' R' if pl['retrograde'] else ''} (дом {pl['house']})" for pl in chart["planets"])
    extra_text = ", ".join(f"{ep['name_ru']} в {ep['sign_ru']}" for ep in chart.get("extra_points", []))
    houses_text = ", ".join(f"Дом {h['number']}: {h['sign_ru' if sru else 'sign']} {h['degree']}°" for h in chart["houses"])
    aspects_text = ", ".join(f"{a['planet1_ru']} {a['symbol']} {a['planet2_ru']} ({a['orb']}°)" for a in chart["aspects"][:5])
    stellium_text = "; ".join(f"{s.get('name_ru' if sru else 'name_en', '?')}: {', '.join(s.get('planets', []))}" for s in chart.get("stelliums", [])) or "нет"

    transits_text = ""
    if req.section == "transits":
        now = datetime.utcnow()
        t_subj = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)
        pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
        actives = []
        for k in pkeys:
            tp = _extract_planet(t_subj, k)
            for np_item in chart["planets"]:
                diff = abs(tp["abs_pos"] - np_item["abs_pos"])
                if diff > 180: diff = 360 - diff
                for angle, _, _, name_ru, _, sym in ASPECT_TYPES:
                    if abs(diff - angle) <= 3:
                        actives.append(f"Транзит {tp['name_ru']} {sym} натал. {np_item['name_ru']} ({round(abs(diff-angle),1)}°)")
                        break
        transits_text = "; ".join(actives[:5]) or "Нет точных транзитов"

    prompt = template.format(sun=sun_s, moon=moon_s, asc=asc_s, planets_text=planets_text,
                             extra_text=extra_text or "нет", houses_text=houses_text,
                             aspects_text=aspects_text, transits_text=transits_text, stellium_text=stellium_text)
    prompt += lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "natal_interpret", 2, 20)
    sys = system_prompt(req.lang) + lang_enforce(req.lang)
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=1400, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
