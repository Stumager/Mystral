import json
import os
import tempfile
from datetime import datetime
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
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
    "true_node": "Сев. узел", "chiron": "Хирон",
}

ASPECT_TYPES = [
    (0, 8, "conjunction", "Соединение", "☌"),
    (60, 6, "sextile", "Секстиль", "⚹"),
    (90, 8, "square", "Квадрат", "□"),
    (120, 8, "trine", "Трин", "△"),
    (180, 8, "opposition", "Оппозиция", "☍"),
]

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


def _sign_from_abs(abs_pos: float) -> str:
    return SIGN_ORDER[int(abs_pos / 30) % 12]


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


def _get_abs_pos(p) -> float:
    abs_pos = getattr(p, "abs_pos", None)
    if abs_pos is not None:
        return float(abs_pos)
    sign = _normalize_sign(p.sign)
    idx = SIGN_ORDER.index(sign) if sign in SIGN_ORDER else 0
    return idx * 30 + p.position


def _extract_planet(subj: AstrologicalSubject, key: str, ptype: str = "planet") -> dict | None:
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
            "symbol": PLANET_SYMBOLS.get(key, "?"),
            "sign": sign_full,
            "sign_ru": _ru(p.sign),
            "degree": round(float(getattr(p, "position", 0)), 1),
            "abs_pos": round(_get_abs_pos(p), 1),
            "house": house,
            "retrograde": bool(getattr(p, "retrograde", False)),
            "type": ptype,
        }
    except Exception:
        return None


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
                    aspects.append({
                        "planet1": p1["name"], "planet1_ru": p1["name_ru"],
                        "planet2": p2["name"], "planet2_ru": p2["name_ru"],
                        "type": atype, "name_ru": name_ru, "symbol": symbol,
                        "orb": round(orb, 1), "harmony": atype in ("trine", "sextile"),
                    })
                    break
    aspects.sort(key=lambda a: a["orb"])
    return aspects


def build_full_chart(subj: AstrologicalSubject) -> dict:
    planet_keys = ["sun", "moon", "mercury", "venus", "mars",
                   "jupiter", "saturn", "uranus", "neptune", "pluto"]
    planets = [p for p in (_extract_planet(subj, k) for k in planet_keys) if p is not None]

    # Extra points: True Node, Chiron
    extra = []
    node = _extract_planet(subj, "true_node", "node")
    if node is None:
        for attr in ["mean_node", "north_node"]:
            node = _extract_planet(subj, attr, "node")
            if node:
                node["name"] = "true_node"
                node["name_ru"] = "Сев. узел"
                node["symbol"] = "☊"
                break
    if node:
        extra.append(node)
        south_abs = (node["abs_pos"] + 180) % 360
        south_sign = _sign_from_abs(south_abs)
        extra.append({
            "name": "south_node", "name_ru": "Юж. узел", "symbol": "☋",
            "sign": south_sign, "sign_ru": _ru(south_sign),
            "degree": round(south_abs % 30, 1), "abs_pos": round(south_abs, 1),
            "house": None, "retrograde": False, "type": "node",
        })

    chiron = _extract_planet(subj, "chiron", "asteroid")
    if chiron:
        extra.append(chiron)

    all_planets = planets + extra
    aspects = _calc_aspects(planets)

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
                "sign_ru": _ru(h.sign), "degree": round(float(getattr(h, "position", 0)), 1),
            })
        except Exception:
            houses.append({"number": i, "sign": "Aries", "sign_ru": "Овен", "degree": 0})

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
                "sign": pof_sign, "sign_ru": _ru(pof_sign),
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
            names = [p["name_ru"] for p in planets if p["sign"] == s]
            stelliums.append({"type": "sign", "name": _ru(s), "planets": names})
    house_groups: dict[int, list[str]] = {}
    for p in planets:
        if p["house"]:
            house_groups.setdefault(p["house"], []).append(p["name_ru"])
    for h, ps in house_groups.items():
        if len(ps) >= 3:
            stelliums.append({"type": "house", "name": f"Дом {h}", "planets": ps})

    dominant_sign = max(sign_count, key=sign_count.get) if sign_count else ""

    try:
        asc = {"sign": _normalize_sign(subj.first_house.sign),
               "sign_ru": _ru(subj.first_house.sign),
               "degree": round(float(subj.first_house.position), 1)}
    except Exception:
        asc = houses[0] if houses else {"sign": "Aries", "sign_ru": "Овен", "degree": 0}

    try:
        mc = {"sign": _normalize_sign(subj.tenth_house.sign),
              "sign_ru": _ru(subj.tenth_house.sign),
              "degree": round(float(subj.tenth_house.position), 1)}
    except Exception:
        mc = houses[9] if len(houses) > 9 else {"sign": "Aries", "sign_ru": "Овен", "degree": 0}

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
    }


class NatalRequest(BaseModel):
    name: str; year: int; month: int; day: int
    hour: int = 12; minute: int = 0; city: str; lang: str = "ru"


class InterpretRequest(NatalRequest):
    section: str = "personality"


@router.post("/natal/calculate")
async def natal_calculate(req: NatalRequest):
    lat, lon = await geocode_city(req.city)
    try:
        subj = _build_subject(req.name, req.year, req.month, req.day, req.hour, req.minute, lat, lon)
        return build_full_chart(subj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")


@router.post("/natal/svg")
async def natal_svg(req: NatalRequest):
    lat, lon = await geocode_city(req.city)
    try:
        from kerykeion import KerykeionChartSVG
        subj = _build_subject(req.name, req.year, req.month, req.day, req.hour, req.minute, lat, lon)
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
    lat, lon = await geocode_city(req.city)
    natal = _build_subject(req.name, req.year, req.month, req.day, req.hour, req.minute, lat, lon)
    now = datetime.utcnow()
    transit = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)

    pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    natal_planets = [_extract_planet(natal, k) for k in pkeys]
    transit_planets = [_extract_planet(transit, k) for k in pkeys]

    active = []
    for tp in transit_planets:
        for np in natal_planets:
            diff = abs(tp["abs_pos"] - np["abs_pos"])
            if diff > 180: diff = 360 - diff
            for angle, _, atype, name_ru, symbol in ASPECT_TYPES:
                orb = abs(diff - angle)
                if orb <= 3:
                    active.append({
                        "transit_planet": tp["name_ru"], "transit_sign": tp["sign_ru"],
                        "natal_planet": np["name_ru"], "natal_sign": np["sign_ru"],
                        "aspect": name_ru, "aspect_symbol": symbol, "orb": round(orb, 1),
                    })
                    break
    active.sort(key=lambda a: a["orb"])
    return {"transits": active[:5], "date": now.isoformat()}


SECTION_PROMPTS_RU = {
    "personality": "Проанализируй Солнце в {sun}, Луну в {moon}, Асцендент в {asc} как единую систему.\nКак эти три энергии взаимодействуют? Где конфликт, где гармония?\nОбращайся на 'ты'. 120-150 слов.",
    "planets": "Планеты: {planets_text}.\nДополнительно: {extra_text}.\nКакая планета самая сильная и почему? Ретроградные — на что обратить внимание?\n120-150 слов. Конкретно.",
    "houses": "Дома: {houses_text}.\nСтеллиумы: {stellium_text}.\nКакие дома наполнены? Где акцент жизни? Пустые — что значит?\n120-150 слов.",
    "aspects": "Топ аспекты: {aspects_text}.\nОбъясни влияние каждого на жизнь конкретно. Какой аспект самый мощный?\n120-150 слов.",
    "transits": "Активные транзиты на сегодня: {transits_text}.\nЧто это значит прямо сейчас? Практический совет.\n100-120 слов.",
}
SECTION_PROMPTS_EN = {
    "personality": "Analyze Sun in {sun}, Moon in {moon}, Ascendant in {asc} as a unified system.\nHow do these three energies interact? Where's conflict, where's harmony?\nUse 'you'. 120-150 words.",
    "planets": "Planets: {planets_text}.\nExtra: {extra_text}.\nWhich planet is strongest and why? Retrograde — what to watch for?\n120-150 words. Be specific.",
    "houses": "Houses: {houses_text}.\nStelliums: {stellium_text}.\nWhich houses are packed? Life focus? Empty houses — meaning?\n120-150 words.",
    "aspects": "Top aspects: {aspects_text}.\nExplain each aspect's impact on life specifically. Which is most powerful?\n120-150 words.",
    "transits": "Active transits today: {transits_text}.\nWhat does this mean right now? Practical advice.\n100-120 words.",
}


@router.post("/natal/interpret")
async def natal_interpret(req: InterpretRequest, current_user: User = Depends(get_current_user)):
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

    sru = req.lang == "ru"
    p = chart.get("planets", [])
    sun_s = p[0]["sign_ru" if sru else "sign"] if len(p) > 0 else "?"
    moon_s = p[1]["sign_ru" if sru else "sign"] if len(p) > 1 else "?"
    asc_s = chart.get("ascendant", {}).get("sign_ru" if sru else "sign", "?")
    planets_text = ", ".join(f"{p['name_ru' if sru else 'name']} в {p['sign_ru' if sru else 'sign']}{' R' if p['retrograde'] else ''} (дом {p['house']})" for p in chart["planets"])
    extra_text = ", ".join(f"{p['name_ru']} в {p['sign_ru']}" for p in chart.get("extra_points", []))
    houses_text = ", ".join(f"Дом {h['number']}: {h['sign_ru' if sru else 'sign']} {h['degree']}°" for h in chart["houses"])
    aspects_text = ", ".join(f"{a['planet1_ru']} {a['symbol']} {a['planet2_ru']} ({a['orb']}°)" for a in chart["aspects"][:5])
    stellium_text = "; ".join(f"{s['name']}: {', '.join(s['planets'])}" for s in chart.get("stelliums", [])) or "нет"

    transits_text = ""
    if req.section == "transits":
        now = datetime.utcnow()
        t_subj = _build_subject("Transit", now.year, now.month, now.day, now.hour, now.minute, lat, lon)
        pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
        actives = []
        for k in pkeys:
            tp = _extract_planet(t_subj, k)
            for np in chart["planets"]:
                diff = abs(tp["abs_pos"] - np["abs_pos"])
                if diff > 180: diff = 360 - diff
                for angle, _, _, name_ru, sym in ASPECT_TYPES:
                    if abs(diff - angle) <= 3:
                        actives.append(f"Транзит {tp['name_ru']} {sym} натал. {np['name_ru']} ({round(abs(diff-angle),1)}°)")
                        break
        transits_text = "; ".join(actives[:5]) or "Нет точных транзитов"

    prompt = template.format(sun=sun_s, moon=moon_s, asc=asc_s, planets_text=planets_text,
                             extra_text=extra_text or "нет", houses_text=houses_text,
                             aspects_text=aspects_text, transits_text=transits_text, stellium_text=stellium_text)

    lang_enforce = "Отвечай ТОЛЬКО на русском. Обращайся на 'ты'." if sru else "Answer ONLY in English. Use 'you'."
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
