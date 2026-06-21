import json
import os
from datetime import datetime
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from kerykeion import AstrologicalSubject
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.prompts import system_prompt
from app.models.user import User

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

SIGNS_RU = {
    "Ari": "Овен", "Aries": "Овен", "Tau": "Телец", "Taurus": "Телец",
    "Gem": "Близнецы", "Gemini": "Близнецы", "Can": "Рак", "Cancer": "Рак",
    "Leo": "Лев", "Vir": "Дева", "Virgo": "Дева", "Lib": "Весы", "Libra": "Весы",
    "Sco": "Скорпион", "Scorpio": "Скорпион", "Sag": "Стрелец", "Sagittarius": "Стрелец",
    "Cap": "Козерог", "Capricorn": "Козерог", "Aqu": "Водолей", "Aquarius": "Водолей",
    "Pis": "Рыбы", "Pisces": "Рыбы",
}

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
}
PLANET_NAMES_RU = {
    "sun": "Солнце", "moon": "Луна", "mercury": "Меркурий", "venus": "Венера",
    "mars": "Марс", "jupiter": "Юпитер", "saturn": "Сатурн",
    "uranus": "Уран", "neptune": "Нептун", "pluto": "Плутон",
}

ASPECT_TYPES = [
    (0, 8, "conjunction", "Соединение", "☌"),
    (60, 6, "sextile", "Секстиль", "⚹"),
    (90, 8, "square", "Квадрат", "□"),
    (120, 8, "trine", "Трин", "△"),
    (180, 8, "opposition", "Оппозиция", "☍"),
]


def _ru(sign: str) -> str:
    return SIGNS_RU.get(sign, SIGNS_RU.get(sign[:3], sign))


def _normalize_sign(sign: str) -> str:
    for full in ELEMENTS:
        if sign.startswith(full[:3]):
            return full
    return sign


async def geocode_city(city: str) -> tuple[float, float]:
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "Mystral/1.0"},
        )
    data = resp.json()
    if not data:
        raise HTTPException(status_code=422, detail=f"City not found: {city}")
    return float(data[0]["lat"]), float(data[0]["lon"])


def _build_subject(name: str, year: int, month: int, day: int,
                   hour: int, minute: int, lat: float, lon: float) -> AstrologicalSubject:
    return AstrologicalSubject(
        name, year, month, day, hour, minute,
        lng=lon, lat=lat, tz_str="UTC", online=False,
    )


HOUSE_NUM = {
    "First_House": 1, "Second_House": 2, "Third_House": 3, "Fourth_House": 4,
    "Fifth_House": 5, "Sixth_House": 6, "Seventh_House": 7, "Eighth_House": 8,
    "Ninth_House": 9, "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}


def _extract_planet(subj: AstrologicalSubject, key: str) -> dict:
    p = getattr(subj, key)
    sign_full = _normalize_sign(p.sign)
    house_raw = getattr(p, "house", None)
    house = HOUSE_NUM.get(house_raw, house_raw) if isinstance(house_raw, str) else house_raw
    abs_pos = getattr(p, "abs_pos", None)
    if abs_pos is None:
        sign_idx = list(ELEMENTS.keys()).index(sign_full) if sign_full in ELEMENTS else 0
        abs_pos = sign_idx * 30 + p.position
    return {
        "name": key,
        "name_ru": PLANET_NAMES_RU.get(key, key),
        "symbol": PLANET_SYMBOLS.get(key, "?"),
        "sign": sign_full,
        "sign_ru": _ru(p.sign),
        "degree": round(p.position, 1),
        "abs_pos": round(abs_pos, 1),
        "house": house,
        "retrograde": bool(getattr(p, "retrograde", False)),
    }


def _calc_aspects(planets: list[dict]) -> list[dict]:
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            diff = abs(p1["abs_pos"] - p2["abs_pos"])
            if diff > 180:
                diff = 360 - diff
            for angle, max_orb, atype, name_ru, symbol in ASPECT_TYPES:
                orb = abs(diff - angle)
                if orb <= max_orb:
                    harmony = atype in ("trine", "sextile")
                    aspects.append({
                        "planet1": p1["name"],
                        "planet1_ru": p1["name_ru"],
                        "planet2": p2["name"],
                        "planet2_ru": p2["name_ru"],
                        "type": atype,
                        "name_ru": name_ru,
                        "symbol": symbol,
                        "orb": round(orb, 1),
                        "harmony": harmony,
                    })
                    break
    aspects.sort(key=lambda a: a["orb"])
    return aspects


def build_full_chart(subj: AstrologicalSubject) -> dict:
    planet_keys = ["sun", "moon", "mercury", "venus", "mars",
                   "jupiter", "saturn", "uranus", "neptune", "pluto"]
    planets = [_extract_planet(subj, k) for k in planet_keys]
    aspects = _calc_aspects(planets)

    house_attrs = ["first_house", "second_house", "third_house", "fourth_house",
                   "fifth_house", "sixth_house", "seventh_house", "eighth_house",
                   "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"]
    houses = []
    for i, attr in enumerate(house_attrs, 1):
        h = getattr(subj, attr)
        houses.append({
            "number": i,
            "sign": _normalize_sign(h.sign),
            "sign_ru": _ru(h.sign),
            "degree": round(h.position, 1),
        })

    el = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    mod = {"cardinal": 0, "fixed": 0, "mutable": 0}
    sign_count: dict[str, int] = {}
    for p in planets:
        e = ELEMENTS.get(p["sign"], "")
        m = MODALITIES.get(p["sign"], "")
        if e:
            el[e] += 1
        if m:
            mod[m] += 1
        sign_count[p["sign"]] = sign_count.get(p["sign"], 0) + 1

    dominant_sign = max(sign_count, key=sign_count.get) if sign_count else ""

    return {
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "ascendant": {"sign": planets[0]["sign"] if not houses else _normalize_sign(subj.first_house.sign),
                      "sign_ru": _ru(subj.first_house.sign),
                      "degree": round(subj.first_house.position, 1)},
        "midheaven": {"sign": _normalize_sign(subj.tenth_house.sign),
                      "sign_ru": _ru(subj.tenth_house.sign),
                      "degree": round(subj.tenth_house.position, 1)},
        "element_balance": el,
        "modality_balance": mod,
        "dominant_sign": dominant_sign,
        "dominant_sign_ru": _ru(dominant_sign) if dominant_sign else "",
    }


class NatalRequest(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    city: str
    lang: str = "ru"


class InterpretRequest(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    city: str
    lang: str = "ru"
    section: str = "personality"


@router.post("/natal/calculate")
async def natal_calculate(req: NatalRequest):
    lat, lon = await geocode_city(req.city)
    try:
        subj = _build_subject(req.name, req.year, req.month, req.day, req.hour, req.minute, lat, lon)
        return build_full_chart(subj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")


@router.post("/natal/transits")
async def natal_transits(
    req: NatalRequest,
    current_user: User = Depends(get_current_user),
):
    lat, lon = await geocode_city(req.city)
    natal = _build_subject(req.name, req.year, req.month, req.day, req.hour, req.minute, lat, lon)
    now = datetime.utcnow()
    transit = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)

    natal_planets = [_extract_planet(natal, k) for k in
                     ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]]
    transit_planets = [_extract_planet(transit, k) for k in
                       ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]]

    active = []
    for tp in transit_planets:
        for np in natal_planets:
            diff = abs(tp["abs_pos"] - np["abs_pos"])
            if diff > 180:
                diff = 360 - diff
            for angle, _, atype, name_ru, symbol in ASPECT_TYPES:
                orb = abs(diff - angle)
                if orb <= 3:
                    active.append({
                        "transit_planet": tp["name_ru"],
                        "transit_sign": tp["sign_ru"],
                        "natal_planet": np["name_ru"],
                        "natal_sign": np["sign_ru"],
                        "aspect": name_ru,
                        "aspect_symbol": symbol,
                        "orb": round(orb, 1),
                    })
                    break
    active.sort(key=lambda a: a["orb"])
    return {"transits": active[:5], "date": now.isoformat()}


SECTION_PROMPTS_RU = {
    "personality": (
        "Проанализируй Солнце в {sun}, Луну в {moon}, Асцендент в {asc} как единую систему.\n"
        "Как эти три энергии взаимодействуют? Где конфликт, где гармония?\n"
        "Обращайся на 'ты'. 120-150 слов."
    ),
    "planets": (
        "Планеты: {planets_text}.\n"
        "Какая планета самая сильная и почему? Ретроградные планеты — на что обратить внимание?\n"
        "120-150 слов. Конкретно."
    ),
    "houses": (
        "Дома: {houses_text}.\n"
        "Какие дома наполнены (3+ планеты)? Где акцент жизни? Какие пустые — что это значит?\n"
        "120-150 слов."
    ),
    "aspects": (
        "Топ аспекты: {aspects_text}.\n"
        "Объясни влияние каждого на жизнь конкретно. Какой аспект самый мощный?\n"
        "120-150 слов."
    ),
    "transits": (
        "Активные транзиты на сегодня: {transits_text}.\n"
        "Что это значит для человека прямо сейчас? Практический совет.\n"
        "100-120 слов."
    ),
}

SECTION_PROMPTS_EN = {
    "personality": (
        "Analyze Sun in {sun}, Moon in {moon}, Ascendant in {asc} as a unified system.\n"
        "How do these three energies interact? Where's the conflict, where's the harmony?\n"
        "Use 'you'. 120-150 words."
    ),
    "planets": (
        "Planets: {planets_text}.\n"
        "Which planet is strongest and why? Retrograde planets — what to watch for?\n"
        "120-150 words. Be specific."
    ),
    "houses": (
        "Houses: {houses_text}.\n"
        "Which houses are packed (3+ planets)? Life focus? Empty houses — what does it mean?\n"
        "120-150 words."
    ),
    "aspects": (
        "Top aspects: {aspects_text}.\n"
        "Explain each aspect's impact on life specifically. Which is most powerful?\n"
        "120-150 words."
    ),
    "transits": (
        "Active transits today: {transits_text}.\n"
        "What does this mean right now? Practical advice.\n"
        "100-120 words."
    ),
}


@router.post("/natal/interpret")
async def natal_interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
):
    if req.section != "personality" and current_user.subscription_tier == "free":
        raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    if current_user.subscription_tier == "free":
        key = f"natal_count:{current_user.id}"
        count = await redis_client.incr(key)
        if count > 3:
            raise HTTPException(status_code=402, detail="FREE_LIMIT_REACHED")

    lat, lon = await geocode_city(req.city)
    subj = _build_subject(req.name, req.year, req.month, req.day, req.hour, req.minute, lat, lon)
    chart = build_full_chart(subj)

    templates = SECTION_PROMPTS_RU if req.lang == "ru" else SECTION_PROMPTS_EN
    template = templates.get(req.section, templates["personality"])

    sun_sign = chart["planets"][0]["sign_ru"] if req.lang == "ru" else chart["planets"][0]["sign"]
    moon_sign = chart["planets"][1]["sign_ru"] if req.lang == "ru" else chart["planets"][1]["sign"]
    asc_sign = chart["ascendant"]["sign_ru"] if req.lang == "ru" else chart["ascendant"]["sign"]

    planets_text = ", ".join(
        f"{p['name_ru'] if req.lang == 'ru' else p['name']} в {p['sign_ru'] if req.lang == 'ru' else p['sign']}"
        f"{' R' if p['retrograde'] else ''} (дом {p['house']})"
        for p in chart["planets"]
    )

    houses_text = ", ".join(
        f"Дом {h['number']}: {h['sign_ru'] if req.lang == 'ru' else h['sign']}"
        for h in chart["houses"]
    )

    aspects_text = ", ".join(
        f"{a['planet1_ru']} {a['symbol']} {a['planet2_ru']} (орб {a['orb']}°)"
        for a in chart["aspects"][:5]
    )

    transits_text = ""
    if req.section == "transits":
        now = datetime.utcnow()
        transit_subj = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)
        natal_planets = [_extract_planet(subj, k) for k in
                         ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]]
        transit_planets = [_extract_planet(transit_subj, k) for k in
                           ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]]
        actives = []
        for tp in transit_planets:
            for np in natal_planets:
                diff = abs(tp["abs_pos"] - np["abs_pos"])
                if diff > 180:
                    diff = 360 - diff
                for angle, _, atype, name_ru, symbol in ASPECT_TYPES:
                    orb = abs(diff - angle)
                    if orb <= 3:
                        actives.append(f"Транзит {tp['name_ru']} {symbol} натал. {np['name_ru']} (орб {round(orb, 1)}°)")
                        break
        transits_text = "; ".join(actives[:5]) or "Нет точных транзитов"

    prompt = template.format(
        sun=sun_sign, moon=moon_sign, asc=asc_sign,
        planets_text=planets_text, houses_text=houses_text,
        aspects_text=aspects_text, transits_text=transits_text,
    )

    lang_enforce = "Отвечай ТОЛЬКО на русском. Обращайся на 'ты'." if req.lang == "ru" else "Answer ONLY in English. Use 'you'."
    sys = system_prompt(req.lang) + f" {lang_enforce}"

    async def generate():
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": prompt}],
            stream=True, max_tokens=400,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'text': delta})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
