import json
import os
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import lang_enforce, system_prompt
from app.core.structural_i18n import localized_field
from app.data.compatibility_i18n import CHINESE_I18N, ELEMENTS_I18N, SIGNS_I18N
from app.models.user import User, UserPartner, UserProfile

router = APIRouter()

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
            "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
ELEMENTS = ["fire", "earth", "air", "water"]
ELEMENTS_RU = ["Огонь", "Земля", "Воздух", "Вода"]
ELEMENTS_EN = ["Fire", "Earth", "Air", "Water"]

CHINESE = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
           "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
CHINESE_RU = ["Крыса", "Бык", "Тигр", "Кролик", "Дракон", "Змея",
              "Лошадь", "Коза", "Обезьяна", "Петух", "Собака", "Свинья"]
CHINESE_EMOJI = ["🐀", "🐂", "🐅", "🐇", "🐉", "🐍", "🐎", "🐐", "🐒", "🐓", "🐕", "🐖"]


# TZ-080: these used to be a plain `RU[idx] if ru else EN[idx]` ternary at
# every call site, which silently collapsed ES/PT/TR/UK to English. Route
# through the i18n modules so those four languages get real labels once
# generated, with English as the fallback until then.
def _sign_name(idx: int, lang: str) -> str:
    if lang == "ru":
        return SIGNS_RU[idx]
    return localized_field(SIGNS_I18N, lang, str(idx), "name", SIGNS[idx])


def _element_name(idx: int, lang: str) -> str:
    if lang == "ru":
        return ELEMENTS_RU[idx]
    return localized_field(ELEMENTS_I18N, lang, str(idx), "name", ELEMENTS_EN[idx])


def _chinese_name(idx: int, lang: str) -> str:
    if lang == "ru":
        return CHINESE_RU[idx]
    return localized_field(CHINESE_I18N, lang, str(idx), "name", CHINESE[idx])

SIGN_RANGES = [
    (9, 1, 1, 1, 19), (10, 1, 20, 2, 18), (11, 2, 19, 3, 20),
    (0, 3, 21, 4, 19), (1, 4, 20, 5, 20), (2, 5, 21, 6, 20),
    (3, 6, 21, 7, 22), (4, 7, 23, 8, 22), (5, 8, 23, 9, 22),
    (6, 9, 23, 10, 22), (7, 10, 23, 11, 21), (8, 11, 22, 12, 21),
    (9, 12, 22, 12, 31),
]


def _sign_idx(d: date) -> int:
    m, day = d.month, d.day
    for idx, fm, fd, tm, td in SIGN_RANGES:
        if (m > fm or (m == fm and day >= fd)) and (m < tm or (m == tm and day <= td)):
            return idx
    return 9


def _element_idx(sign_idx: int) -> int:
    return sign_idx % 4


def _chinese_idx(year: int) -> int:
    return (year - 4) % 12


def _life_path(d: date) -> int:
    n = sum(int(c) for c in d.isoformat().replace("-", ""))
    while n > 9 and n not in (11, 22):
        n = sum(int(c) for c in str(n))
    return n


def _sign_compat(i1: int, i2: int) -> int:
    if i1 == i2: return 75
    e1, e2 = i1 % 4, i2 % 4
    base = 42
    if e1 == e2: base = 88
    elif {e1, e2} in ({0, 2}, {1, 3}): base = 76
    v = ((i1 + 1) * (i2 + 1)) % 11 - 5
    return max(25, min(98, base + v))


ELEMENT_MATRIX = {
    (0, 0): 85, (1, 1): 82, (2, 2): 80, (3, 3): 90,
    (0, 2): 78, (2, 0): 78, (1, 3): 82, (3, 1): 82,
    (0, 1): 45, (1, 0): 45, (0, 3): 35, (3, 0): 35,
    (2, 3): 42, (3, 2): 42, (2, 1): 48, (1, 2): 48,
}

CHINESE_COMPAT = {}
FRIEND_TRIADS = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3, 7, 11}]
CLASH = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
for a in range(12):
    for b in range(12):
        if a == b:
            CHINESE_COMPAT[(a, b)] = 72
        elif any(a in t and b in t for t in FRIEND_TRIADS):
            CHINESE_COMPAT[(a, b)] = 88
        elif (a, b) in CLASH or (b, a) in CLASH:
            CHINESE_COMPAT[(a, b)] = 32
        else:
            CHINESE_COMPAT[(a, b)] = 55 + ((a + b) % 15)

NUM_COMPAT = {}
for a in range(1, 10):
    for b in range(1, 10):
        if a == b: NUM_COMPAT[(a, b)] = 80
        elif {a, b} in ({1, 5}, {2, 4}, {3, 6}, {4, 8}, {1, 9}): NUM_COMPAT[(a, b)] = 88
        elif {a, b} in ({4, 5}, {1, 8}, {3, 7}): NUM_COMPAT[(a, b)] = 38
        else: NUM_COMPAT[(a, b)] = 55 + ((a * b) % 20)


_DESCS = {
    "ru": ("Гармоничная пара с глубоким взаимопониманием.", "Интересный союз с потенциалом роста.", "Непростое сочетание, требующее работы над собой."),
    "en": ("A harmonious pair with deep mutual understanding.", "An interesting union with growth potential.", "A challenging combination requiring patience and self-work."),
    "es": ("Una pareja armoniosa con profunda comprensión mutua.", "Una unión interesante con potencial de crecimiento.", "Una combinación desafiante que requiere paciencia y trabajo personal."),
    "pt": ("Um par harmonioso com profunda compreensão mútua.", "Uma união interessante com potencial de crescimento.", "Uma combinação desafiadora que requer paciência e autoconhecimento."),
    "tr": ("Derin karşılıklı anlayışa sahip uyumlu bir çift.", "Büyüme potansiyeli olan ilginç bir birliktelik.", "Sabır ve öz çalışma gerektiren zorlu bir kombinasyon."),
    "uk": ("Гармонійна пара з глибоким взаєморозумінням.", "Цікавий союз із потенціалом зростання.", "Непросте поєднання, що потребує роботи над собою."),
}


def _desc(score: int, lang: str) -> str:
    high, mid, low = _DESCS.get(lang, _DESCS["en"])
    if score >= 75:
        return high
    if score >= 50:
        return mid
    return low


# ---- Partner CRUD ----

def _parse_partner_id(partner_id: str) -> UUID:
    try:
        return UUID(partner_id)
    except ValueError:
        raise HTTPException(422, "Invalid partner_id")


class PartnerCreate(BaseModel):
    name: str
    birth_date: str
    birth_hour: Optional[int] = None
    birth_minute: Optional[int] = None
    birth_city: Optional[str] = None


@router.get("/partners")
async def list_partners(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(UserPartner).where(UserPartner.user_id == current_user.id)
        .order_by(UserPartner.created_at.desc())
    )
    partners = result.all()
    return [{
        "id": str(p.id), "name": p.label, "birth_date": p.birth_date.isoformat(),
        "zodiac_sign": p.zodiac_sign, "zodiac_sign_ru": SIGNS_RU[SIGNS.index(p.zodiac_sign)] if p.zodiac_sign in SIGNS else p.zodiac_sign,
        "zodiac_symbol": SYMBOLS[SIGNS.index(p.zodiac_sign)] if p.zodiac_sign in SIGNS else "?",
        "chinese_sign": p.chinese_sign, "life_path": p.life_path,
        "has_time": p.birth_time is not None, "has_city": p.birth_city is not None,
    } for p in partners]


@router.post("/partners")
async def create_partner(
    req: PartnerCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.exec(
        select(UserPartner).where(UserPartner.user_id == current_user.id)
    )
    if current_user.subscription_tier == "free" and len(existing.all()) >= 3:
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    bd = date.fromisoformat(req.birth_date)
    si = _sign_idx(bd)
    bt = None
    if req.birth_hour is not None:
        from datetime import time
        bt = time(req.birth_hour, req.birth_minute or 0)

    lat, lng = None, None
    if req.birth_city:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as http:
                r = await http.get("https://nominatim.openstreetmap.org/search",
                                   params={"q": req.birth_city, "format": "json", "limit": 1},
                                   headers={"User-Agent": "Mystral/1.0"})
                data = r.json()
                if data:
                    lat, lng = float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass

    partner = UserPartner(
        user_id=current_user.id, label=req.name, birth_date=bd, birth_time=bt,
        birth_city=req.birth_city, birth_lat=lat, birth_lng=lng,
        zodiac_sign=SIGNS[si], chinese_sign=CHINESE[_chinese_idx(bd.year)],
        life_path=_life_path(bd),
    )
    session.add(partner)
    await session.commit()
    await session.refresh(partner)
    return {"id": str(partner.id), "zodiac_sign": SIGNS[si]}


@router.delete("/partners/{partner_id}")
async def delete_partner(
    partner_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    p = await session.get(UserPartner, _parse_partner_id(partner_id))
    if not p or p.user_id != current_user.id:
        raise HTTPException(404, "Not found")
    await session.delete(p)
    await session.commit()
    return {"ok": True}


# ---- Compatibility Types ----

class CompatTypeRequest(BaseModel):
    partner_id: str
    lang: str = "ru"


async def _get_user_and_partner(req: CompatTypeRequest, user: User, session: AsyncSession):
    profile = await session.exec(select(UserProfile).where(UserProfile.user_id == user.id))
    prof = profile.first()
    if not prof or not prof.birth_date:
        raise HTTPException(400, "Fill your birth date in profile")
    partner = await session.get(UserPartner, _parse_partner_id(req.partner_id))
    if not partner or partner.user_id != user.id:
        raise HTTPException(404, "Partner not found")
    return prof, partner


@router.post("/compatibility/signs")
async def compat_signs(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    i1 = _sign_idx(prof.birth_date)
    i2 = _sign_idx(partner.birth_date)
    score = _sign_compat(i1, i2)
    return {
        "type": "signs", "score": score,
        "user_sign": _sign_name(i1, req.lang), "user_symbol": SYMBOLS[i1],
        "partner_sign": _sign_name(i2, req.lang), "partner_symbol": SYMBOLS[i2],
        "partner_name": partner.label,
        "description": _desc(score, req.lang),
    }


@router.post("/compatibility/elements")
async def compat_elements(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    e1 = _element_idx(_sign_idx(prof.birth_date))
    e2 = _element_idx(_sign_idx(partner.birth_date))
    score = ELEMENT_MATRIX.get((e1, e2), 55)
    return {
        "type": "elements", "score": score,
        "user_element": _element_name(e1, req.lang),
        "partner_element": _element_name(e2, req.lang),
        "partner_name": partner.label,
        "description": _desc(score, req.lang),
    }


@router.post("/compatibility/numerology")
async def compat_numerology(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    n1 = _life_path(prof.birth_date)
    n2 = _life_path(partner.birth_date)
    k1, k2 = min(n1, 9), min(n2, 9)
    score = NUM_COMPAT.get((k1, k2), 55)
    return {
        "type": "numerology", "score": score,
        "user_number": n1, "partner_number": n2,
        "partner_name": partner.label,
        "description": _desc(score, req.lang),
    }


@router.post("/compatibility/chinese")
async def compat_chinese(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    c1 = _chinese_idx(prof.birth_date.year)
    c2 = _chinese_idx(partner.birth_date.year)
    score = CHINESE_COMPAT.get((c1, c2), 55)
    return {
        "type": "chinese", "score": score,
        "user_animal": _chinese_name(c1, req.lang),
        "user_emoji": CHINESE_EMOJI[c1],
        "partner_animal": _chinese_name(c2, req.lang),
        "partner_emoji": CHINESE_EMOJI[c2],
        "partner_name": partner.label,
        "description": _desc(score, req.lang),
    }


@router.post("/compatibility/moon")
async def compat_moon(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    if not prof.birth_time or not partner.birth_time:
        _moon_msgs = {
            "ru": "Для лунной совместимости нужно время рождения обоих",
            "en": "Moon compatibility requires birth time for both",
            "es": "La compatibilidad lunar requiere hora de nacimiento de ambos",
            "pt": "A compatibilidade lunar requer horário de nascimento de ambos",
            "tr": "Ay uyumu için her ikisinin de doğum saati gerekli",
            "uk": "Для місячної сумісності потрібен час народження обох",
        }
        msg = _moon_msgs.get(req.lang, _moon_msgs["en"])
        raise HTTPException(400, msg)

    try:
        from kerykeion import AstrologicalSubject
        from app.api.v1.natal import geocode_city, _normalize_sign, resolve_timezone
        lat1, lon1 = (prof.birth_lat or 55.75), (prof.birth_lng or 37.62)
        s1 = AstrologicalSubject("User", prof.birth_date.year, prof.birth_date.month, prof.birth_date.day,
                                 prof.birth_time.hour, prof.birth_time.minute, lng=lon1, lat=lat1, tz_str=resolve_timezone(lat1, lon1), online=False)
        lat2, lon2 = (partner.birth_lat or 55.75), (partner.birth_lng or 37.62)
        h2, m2 = partner.birth_time.hour, partner.birth_time.minute
        s2 = AstrologicalSubject("Partner", partner.birth_date.year, partner.birth_date.month, partner.birth_date.day,
                                 h2, m2, lng=lon2, lat=lat2, tz_str=resolve_timezone(lat2, lon2), online=False)
        mi1 = SIGNS.index(_normalize_sign(s1.moon.sign)) if _normalize_sign(s1.moon.sign) in SIGNS else 0
        mi2 = SIGNS.index(_normalize_sign(s2.moon.sign)) if _normalize_sign(s2.moon.sign) in SIGNS else 0
        score = _sign_compat(mi1, mi2)
        return {
            "type": "moon", "score": score,
            "user_moon": _sign_name(mi1, req.lang),
            "partner_moon": _sign_name(mi2, req.lang),
            "partner_name": partner.label,
            "description": _desc(score, req.lang),
        }
    except Exception as e:
        raise HTTPException(500, f"Moon calculation failed: {e}")


@router.post("/compatibility/synastry")
async def compat_synastry(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")
    prof, partner = await _get_user_and_partner(req, current_user, session)

    try:
        from kerykeion import AstrologicalSubject
        from app.api.v1.natal import (
            PLANET_NAMES_EN, PLANET_NAMES_RU, _normalize_sign,
            ASPECT_TYPES as NATAL_ASPECTS, resolve_timezone,
        )

        lat1, lon1 = (prof.birth_lat or 55.75), (prof.birth_lng or 37.62)
        s1 = AstrologicalSubject("User", prof.birth_date.year, prof.birth_date.month, prof.birth_date.day,
                                 prof.birth_time.hour if prof.birth_time else 12, prof.birth_time.minute if prof.birth_time else 0,
                                 lng=lon1, lat=lat1, tz_str=resolve_timezone(lat1, lon1), online=False)
        lat2, lon2 = (partner.birth_lat or 55.75), (partner.birth_lng or 37.62)
        s2 = AstrologicalSubject("Partner", partner.birth_date.year, partner.birth_date.month, partner.birth_date.day,
                                 partner.birth_time.hour if partner.birth_time else 12, partner.birth_time.minute if partner.birth_time else 0,
                                 lng=lon2, lat=lat2, tz_str=resolve_timezone(lat2, lon2), online=False)

        # TZ-080: previously a local pnames_ru-only dict + always-Russian
        # "aspect" field, regardless of req.lang. Reuse natal.py's existing
        # bilingual PLANET_NAMES_* instead of duplicating a Russian-only copy.
        ru = req.lang == "ru"
        pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        pnames = PLANET_NAMES_RU if ru else PLANET_NAMES_EN
        aspects = []
        for k1 in pkeys:
            p1 = getattr(s1, k1, None)
            if not p1: continue
            for k2 in pkeys:
                p2 = getattr(s2, k2, None)
                if not p2: continue
                a1 = getattr(p1, "abs_pos", p1.position)
                a2 = getattr(p2, "abs_pos", p2.position)
                diff = abs(float(a1) - float(a2))
                if diff > 180: diff = 360 - diff
                for angle, max_orb, atype, name_ru, name_en, sym in NATAL_ASPECTS:
                    orb = abs(diff - angle)
                    if orb <= 6:
                        aspects.append({
                            "user_planet": pnames.get(k1, k1),
                            "partner_planet": pnames.get(k2, k2),
                            "aspect": name_ru if ru else name_en, "symbol": sym,
                            "orb": round(orb, 1),
                            "harmony": atype in ("trine", "sextile"),
                        })
                        break
        aspects.sort(key=lambda a: a["orb"])
        total = len(aspects)
        harmony_count = sum(1 for a in aspects if a["harmony"])
        score = int((harmony_count / max(total, 1)) * 100) if total else 55
        return {
            "type": "synastry", "score": min(98, max(25, score)),
            "aspects": aspects[:10], "total_aspects": total,
            "partner_name": partner.label,
            "description": _desc(score, req.lang),
        }
    except Exception as e:
        raise HTTPException(500, f"Synastry failed: {e}")


@router.post("/compatibility/overall")
async def compat_overall(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    i1, i2 = _sign_idx(prof.birth_date), _sign_idx(partner.birth_date)
    scores = {
        "signs": _sign_compat(i1, i2),
        "elements": ELEMENT_MATRIX.get((_element_idx(i1), _element_idx(i2)), 55),
        "numerology": NUM_COMPAT.get((min(_life_path(prof.birth_date), 9), min(_life_path(partner.birth_date), 9)), 55),
        "chinese": CHINESE_COMPAT.get((_chinese_idx(prof.birth_date.year), _chinese_idx(partner.birth_date.year)), 55),
    }
    overall = round(sum(scores.values()) / len(scores))
    return {
        "type": "overall", "score": overall, "scores": scores,
        "partner_name": partner.label,
        "user_sign": _sign_name(i1, req.lang), "user_symbol": SYMBOLS[i1],
        "partner_sign": _sign_name(i2, req.lang), "partner_symbol": SYMBOLS[i2],
        "description": _desc(overall, req.lang),
    }


# ---- Interpret ----

class InterpretRequest(BaseModel):
    compat_type: str
    partner_id: str
    score: int = 50
    lang: str = "ru"


# ---- Composite Chart ----

COMPOSITE_PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
COMPOSITE_PLANET_NAMES = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus", "mars": "Mars",
    "jupiter": "Jupiter", "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto",
}
COMPOSITE_PLANET_NAMES_RU = {
    "sun": "Солнце", "moon": "Луна", "mercury": "Меркурий", "venus": "Венера", "mars": "Марс",
    "jupiter": "Юпитер", "saturn": "Сатурн", "uranus": "Уран", "neptune": "Нептун", "pluto": "Плутон",
}
COMPOSITE_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                   "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
COMPOSITE_SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                      "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
COMPOSITE_ELEMENTS = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}
COMPOSITE_MODALITIES = {
    "Aries": "cardinal", "Cancer": "cardinal", "Libra": "cardinal", "Capricorn": "cardinal",
    "Taurus": "fixed", "Leo": "fixed", "Scorpio": "fixed", "Aquarius": "fixed",
    "Gemini": "mutable", "Virgo": "mutable", "Sagittarius": "mutable", "Pisces": "mutable",
}
COMPOSITE_ASPECT_TYPES = [
    (0, 8, "conjunction"), (60, 4, "sextile"), (90, 6, "square"),
    (120, 6, "trine"), (180, 8, "opposition"),
]


def _midpoint(a1: float, a2: float) -> float:
    diff = abs(a1 - a2)
    if diff > 180:
        lo, hi = min(a1, a2), max(a1, a2)
        return ((hi + lo + 360) / 2) % 360
    return (a1 + a2) / 2


def _sign_from_pos(pos: float) -> tuple[str, str, float]:
    idx = int(pos / 30) % 12
    return COMPOSITE_SIGNS[idx], COMPOSITE_SIGNS_RU[idx], round(pos % 30, 1)


def _composite_aspects(planets: list[dict]) -> list[dict]:
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            diff = abs(p1["abs_pos"] - p2["abs_pos"])
            if diff > 180:
                diff = 360 - diff
            for angle, orb_limit, atype in COMPOSITE_ASPECT_TYPES:
                orb = abs(diff - angle)
                if orb <= orb_limit:
                    aspects.append({
                        "planet1": p1["name"], "planet1_ru": p1["name_ru"],
                        "planet2": p2["name"], "planet2_ru": p2["name_ru"],
                        "type": atype, "orb": round(orb, 1),
                    })
                    break
    aspects.sort(key=lambda a: a["orb"])
    return aspects


class CompositeRequest(BaseModel):
    partner_id: str
    lang: str = "ru"


class CompositeInterpretRequest(BaseModel):
    partner_id: str
    section: str = "overview"
    lang: str = "ru"


@router.post("/compatibility/composite")
async def compat_composite(
    req: CompositeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    from sqlmodel import select as sqlselect
    profile_res = await session.exec(sqlselect(UserProfile).where(UserProfile.user_id == current_user.id))
    prof = profile_res.first()
    if not prof or not prof.birth_date:
        return {"error": "incomplete_data", "message": "Заполните дату рождения в Профиле для composite chart."}

    partner = await session.get(UserPartner, _parse_partner_id(req.partner_id))
    if not partner or partner.user_id != current_user.id:
        raise HTTPException(404, "Partner not found")

    if not partner.birth_date:
        return {"error": "incomplete_data", "message": "Для composite chart нужна дата рождения партнёра."}

    try:
        from kerykeion import AstrologicalSubject
        from app.api.v1.natal import _normalize_sign, resolve_timezone

        lat1 = prof.birth_lat or 55.75
        lon1 = prof.birth_lng or 37.62
        lat2 = partner.birth_lat or 55.75
        lon2 = partner.birth_lng or 37.62
        h1 = prof.birth_time.hour if prof.birth_time else 12
        m1 = prof.birth_time.minute if prof.birth_time else 0
        h2 = partner.birth_time.hour if partner.birth_time else 12
        m2 = partner.birth_time.minute if partner.birth_time else 0

        s1 = AstrologicalSubject("P1", prof.birth_date.year, prof.birth_date.month, prof.birth_date.day,
                                 h1, m1, lng=lon1, lat=lat1, tz_str=resolve_timezone(lat1, lon1), online=False)
        s2 = AstrologicalSubject("P2", partner.birth_date.year, partner.birth_date.month, partner.birth_date.day,
                                 h2, m2, lng=lon2, lat=lat2, tz_str=resolve_timezone(lat2, lon2), online=False)

        planets_out = []
        for key in COMPOSITE_PLANETS:
            p1 = getattr(s1, key, None)
            p2 = getattr(s2, key, None)
            if p1 is None or p2 is None:
                continue
            a1 = float(getattr(p1, "abs_pos", 0))
            a2 = float(getattr(p2, "abs_pos", 0))
            comp_pos = _midpoint(a1, a2)
            sign_en, sign_ru, degree = _sign_from_pos(comp_pos)
            planets_out.append({
                "name": COMPOSITE_PLANET_NAMES.get(key, key),
                "name_ru": COMPOSITE_PLANET_NAMES_RU.get(key, key),
                "sign": sign_en, "sign_ru": sign_ru,
                "degree": degree, "abs_pos": round(comp_pos, 1),
            })

        aspects = _composite_aspects(planets_out)

        el = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        mod = {"cardinal": 0, "fixed": 0, "mutable": 0}
        for p in planets_out:
            e = COMPOSITE_ELEMENTS.get(p["sign"], "")
            m = COMPOSITE_MODALITIES.get(p["sign"], "")
            if e: el[e] += 1
            if m: mod[m] += 1

        return {
            "planets": planets_out,
            "aspects": aspects[:10],
            "summary": {"element_balance": el, "modality_balance": mod},
            "partner_name": partner.label,
        }
    except Exception as e:
        raise HTTPException(500, f"Composite calculation failed: {e}")


@router.post("/compatibility/composite/interpret")
async def composite_interpret(
    req: CompositeInterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    from sqlmodel import select as sqlselect
    profile_res = await session.exec(sqlselect(UserProfile).where(UserProfile.user_id == current_user.id))
    prof = profile_res.first()
    if not prof or not prof.birth_date:
        raise HTTPException(400, "No birth data")

    partner = await session.get(UserPartner, _parse_partner_id(req.partner_id))
    if not partner or partner.user_id != current_user.id:
        raise HTTPException(404, "Partner not found")

    try:
        from kerykeion import AstrologicalSubject
        from app.api.v1.natal import resolve_timezone

        lat1 = prof.birth_lat or 55.75; lon1 = prof.birth_lng or 37.62
        lat2 = partner.birth_lat or 55.75; lon2 = partner.birth_lng or 37.62
        h1 = prof.birth_time.hour if prof.birth_time else 12; m1 = prof.birth_time.minute if prof.birth_time else 0
        h2 = partner.birth_time.hour if partner.birth_time else 12; m2 = partner.birth_time.minute if partner.birth_time else 0

        s1 = AstrologicalSubject("P1", prof.birth_date.year, prof.birth_date.month, prof.birth_date.day,
                                 h1, m1, lng=lon1, lat=lat1, tz_str=resolve_timezone(lat1, lon1), online=False)
        s2 = AstrologicalSubject("P2", partner.birth_date.year, partner.birth_date.month, partner.birth_date.day,
                                 h2, m2, lng=lon2, lat=lat2, tz_str=resolve_timezone(lat2, lon2), online=False)

        planets_out = []
        for key in COMPOSITE_PLANETS:
            p1 = getattr(s1, key, None); p2 = getattr(s2, key, None)
            if not p1 or not p2: continue
            comp_pos = _midpoint(float(getattr(p1, "abs_pos", 0)), float(getattr(p2, "abs_pos", 0)))
            sign_en, sign_ru, degree = _sign_from_pos(comp_pos)
            planets_out.append({"key": key, "name": COMPOSITE_PLANET_NAMES.get(key, key),
                                 "name_ru": COMPOSITE_PLANET_NAMES_RU.get(key, key),
                                 "sign": sign_en, "sign_ru": sign_ru, "degree": degree, "abs_pos": round(comp_pos, 1)})

        aspects = _composite_aspects(planets_out)[:5]
        user_name = prof.full_name or current_user.display_name or "Партнёр 1"
        partner_name = partner.label
        sru = req.lang == "ru"

        key_planets = {p["key"]: p for p in planets_out}
        sun_s = (key_planets["sun"]["sign_ru"] if sru else key_planets["sun"]["sign"]) if "sun" in key_planets else "?"
        moon_s = (key_planets["moon"]["sign_ru"] if sru else key_planets["moon"]["sign"]) if "moon" in key_planets else "?"
        venus_s = (key_planets["venus"]["sign_ru"] if sru else key_planets["venus"]["sign"]) if "venus" in key_planets else "?"
        mars_s = (key_planets["mars"]["sign_ru"] if sru else key_planets["mars"]["sign"]) if "mars" in key_planets else "?"

        planets_text = ", ".join(f"{p['name_ru' if sru else 'name']} в {p['sign_ru' if sru else 'sign']} {p['degree']}°" for p in planets_out)
        aspects_text = ", ".join(f"{a['planet1_ru' if sru else 'planet1']} {a['type']} {a['planet2_ru' if sru else 'planet2']} ({a['orb']}°)" for a in aspects)

        PROMPTS = {
            "ru": {
                "overview": f"Composite chart пары {user_name} и {partner_name}.\nСолнце в {sun_s}, Луна в {moon_s}.\nВсе планеты: {planets_text}.\nОпиши эти отношения: ключевые планеты — по одному абзацу на каждую, главный аспект пары, основной вызов, практическая рекомендация. Без лирики. 150-250 слов, без воды.",
                "planets": f"Composite chart: Солнце в {sun_s}, Луна в {moon_s}, Венера в {venus_s}, Марс в {mars_s}.\nРаскрой каждую из этих 4 планет отдельным абзацем: что она говорит об этой паре. Без лирики. 150-250 слов, без воды.",
                "aspects": f"Ключевые аспекты composite chart: {aspects_text}.\nОпредели главный аспект и разбери его влияние на отношения, затем остальные по значимости. Укажи вызов, который создаёт главный аспект. Без лирики. 150-250 слов, без воды.",
                "advice": f"Composite: Солнце в {sun_s}, Луна в {moon_s}, Венера в {venus_s}.\nАспекты: {aspects_text}.\nОпредели главный вызов пары и дай практическую рекомендацию, как его преодолеть. Без лирики. 150-250 слов, без воды.",
            },
            "en": {
                "overview": f"Composite chart for {user_name} and {partner_name}.\nSun in {sun_s}, Moon in {moon_s}.\nAll planets: {planets_text}.\nDescribe this relationship: key planets — one paragraph each, the couple's main aspect, core challenge, practical recommendation. No lyricism. 150-250 words, no filler.",
                "planets": f"Composite chart: Sun in {sun_s}, Moon in {moon_s}, Venus in {venus_s}, Mars in {mars_s}.\nCover each of these 4 planets in its own paragraph: what it says about this couple. No lyricism. 150-250 words, no filler.",
                "aspects": f"Key composite aspects: {aspects_text}.\nIdentify the main aspect and explain its impact on the relationship first, then the rest by significance. State the challenge the main aspect creates. No lyricism. 150-250 words, no filler.",
                "advice": f"Composite: Sun in {sun_s}, Moon in {moon_s}, Venus in {venus_s}.\nAspects: {aspects_text}.\nIdentify the couple's main challenge and give a practical recommendation to work through it. No lyricism. 150-250 words, no filler.",
            },
        }
        lang_prompts = PROMPTS.get(req.lang, PROMPTS["en"])
        prompt = lang_prompts.get(req.section, lang_prompts["overview"]) + lang_enforce(req.lang)

        await check_rate_limit(str(current_user.id), current_user.subscription_tier, "composite_interpret", 5, 50)
        sys = system_prompt(req.lang) + lang_enforce(req.lang)
        msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]
        return StreamingResponse(safe_groq_stream(msgs, max_tokens=900, lang=req.lang),
                                 media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    except Exception as e:
        raise HTTPException(500, f"Composite interpret failed: {e}")


@router.post("/compatibility/interpret")
async def interpret(req: InterpretRequest, current_user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
    if req.compat_type not in ("signs", "elements") and current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    prof, partner = await _get_user_and_partner(
        CompatTypeRequest(partner_id=req.partner_id, lang=req.lang), current_user, session)

    i1, i2 = _sign_idx(prof.birth_date), _sign_idx(partner.birth_date)
    s1, s2 = SIGNS[i1], SIGNS[i2]
    sys = system_prompt(req.lang) + lang_enforce(req.lang)

    if req.lang == "ru":
        prompt = (
            f"Совместимость ({req.compat_type}): {SIGNS_RU[i1]} и {SIGNS_RU[i2]}. Скор: {req.score}%.\n"
            f"Опиши совместимость:\n"
            f"1. В чём сила этой пары\n2. Главный источник конфликтов\n"
            f"3. Практический совет\n"
            f"Называй конкретные ситуации. 150-250 слов, без воды."
        )
    else:
        prompt = (
            f"Compatibility ({req.compat_type}): {s1} and {s2}. Score: {req.score}%.\n"
            f"Describe compatibility:\n1. Pair's strength\n2. Main conflict source\n"
            f"3. Practical tip\n"
            f"Name concrete situations. 150-250 words, no filler."
        )
    prompt += lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "compat_interpret", 5, 50)
    msgs = [{"role": "system", "content": sys}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=700, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
