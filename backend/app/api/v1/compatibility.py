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
from app.core.prompts import system_prompt
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


def _desc(score: int, lang: str) -> str:
    if lang == "ru":
        if score >= 75: return "Гармоничная пара с глубоким взаимопониманием."
        if score >= 50: return "Интересный союз с потенциалом роста."
        return "Непростое сочетание, требующее работы над собой."
    if score >= 75: return "A harmonious pair with deep mutual understanding."
    if score >= 50: return "An interesting union with growth potential."
    return "A challenging combination requiring patience and self-work."


# ---- Partner CRUD ----

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
    p = await session.get(UserPartner, UUID(partner_id))
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
    partner = await session.get(UserPartner, UUID(req.partner_id))
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
    ru = req.lang == "ru"
    return {
        "type": "signs", "score": score,
        "user_sign": SIGNS_RU[i1] if ru else SIGNS[i1], "user_symbol": SYMBOLS[i1],
        "partner_sign": SIGNS_RU[i2] if ru else SIGNS[i2], "partner_symbol": SYMBOLS[i2],
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
    ru = req.lang == "ru"
    return {
        "type": "elements", "score": score,
        "user_element": ELEMENTS_RU[e1] if ru else ELEMENTS_EN[e1],
        "partner_element": ELEMENTS_RU[e2] if ru else ELEMENTS_EN[e2],
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
    ru = req.lang == "ru"
    return {
        "type": "chinese", "score": score,
        "user_animal": CHINESE_RU[c1] if ru else CHINESE[c1],
        "user_emoji": CHINESE_EMOJI[c1],
        "partner_animal": CHINESE_RU[c2] if ru else CHINESE[c2],
        "partner_emoji": CHINESE_EMOJI[c2],
        "partner_name": partner.label,
        "description": _desc(score, req.lang),
    }


@router.post("/compatibility/moon")
async def compat_moon(req: CompatTypeRequest, current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)):
    prof, partner = await _get_user_and_partner(req, current_user, session)
    if not prof.birth_time or not partner.birth_time:
        msg = "Для лунной совместимости нужно время рождения обоих" if req.lang == "ru" else "Moon compatibility requires birth time for both"
        raise HTTPException(400, msg)

    try:
        from kerykeion import AstrologicalSubject
        from app.api.v1.natal import geocode_city, _normalize_sign
        lat1, lon1 = (prof.birth_lat or 55.75), (prof.birth_lng or 37.62)
        s1 = AstrologicalSubject("User", prof.birth_date.year, prof.birth_date.month, prof.birth_date.day,
                                 prof.birth_time.hour, prof.birth_time.minute, lng=lon1, lat=lat1, tz_str="UTC", online=False)
        lat2, lon2 = (partner.birth_lat or 55.75), (partner.birth_lng or 37.62)
        h2, m2 = partner.birth_time.hour, partner.birth_time.minute
        s2 = AstrologicalSubject("Partner", partner.birth_date.year, partner.birth_date.month, partner.birth_date.day,
                                 h2, m2, lng=lon2, lat=lat2, tz_str="UTC", online=False)
        mi1 = SIGNS.index(_normalize_sign(s1.moon.sign)) if _normalize_sign(s1.moon.sign) in SIGNS else 0
        mi2 = SIGNS.index(_normalize_sign(s2.moon.sign)) if _normalize_sign(s2.moon.sign) in SIGNS else 0
        score = _sign_compat(mi1, mi2)
        ru = req.lang == "ru"
        return {
            "type": "moon", "score": score,
            "user_moon": SIGNS_RU[mi1] if ru else SIGNS[mi1],
            "partner_moon": SIGNS_RU[mi2] if ru else SIGNS[mi2],
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
        from app.api.v1.natal import _normalize_sign, ASPECT_TYPES as NATAL_ASPECTS

        lat1, lon1 = (prof.birth_lat or 55.75), (prof.birth_lng or 37.62)
        s1 = AstrologicalSubject("User", prof.birth_date.year, prof.birth_date.month, prof.birth_date.day,
                                 prof.birth_time.hour if prof.birth_time else 12, prof.birth_time.minute if prof.birth_time else 0,
                                 lng=lon1, lat=lat1, tz_str="UTC", online=False)
        lat2, lon2 = (partner.birth_lat or 55.75), (partner.birth_lng or 37.62)
        s2 = AstrologicalSubject("Partner", partner.birth_date.year, partner.birth_date.month, partner.birth_date.day,
                                 partner.birth_time.hour if partner.birth_time else 12, partner.birth_time.minute if partner.birth_time else 0,
                                 lng=lon2, lat=lat2, tz_str="UTC", online=False)

        pkeys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        pnames_ru = {"sun": "Солнце", "moon": "Луна", "mercury": "Меркурий", "venus": "Венера",
                     "mars": "Марс", "jupiter": "Юпитер", "saturn": "Сатурн"}
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
                for angle, max_orb, atype, name_ru, sym in NATAL_ASPECTS:
                    orb = abs(diff - angle)
                    if orb <= 6:
                        aspects.append({
                            "user_planet": pnames_ru.get(k1, k1),
                            "partner_planet": pnames_ru.get(k2, k2),
                            "aspect": name_ru, "symbol": sym,
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
    ru = req.lang == "ru"
    return {
        "type": "overall", "score": overall, "scores": scores,
        "partner_name": partner.label,
        "user_sign": SIGNS_RU[i1] if ru else SIGNS[i1], "user_symbol": SYMBOLS[i1],
        "partner_sign": SIGNS_RU[i2] if ru else SIGNS[i2], "partner_symbol": SYMBOLS[i2],
        "description": _desc(overall, req.lang),
    }


# ---- Interpret ----

class InterpretRequest(BaseModel):
    compat_type: str
    partner_id: str
    score: int = 50
    lang: str = "ru"


@router.post("/compatibility/interpret")
async def interpret(req: InterpretRequest, current_user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
    if req.compat_type not in ("signs", "elements") and current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    prof, partner = await _get_user_and_partner(
        CompatTypeRequest(partner_id=req.partner_id, lang=req.lang), current_user, session)

    i1, i2 = _sign_idx(prof.birth_date), _sign_idx(partner.birth_date)
    s1, s2 = SIGNS[i1], SIGNS[i2]
    sys = system_prompt(req.lang)
    lang_enforce = " Отвечай ТОЛЬКО на русском." if req.lang == "ru" else " Answer ONLY in English."

    if req.lang == "ru":
        prompt = (
            f"Совместимость ({req.compat_type}): {SIGNS_RU[i1]} и {SIGNS_RU[i2]}. Скор: {req.score}%.\n"
            f"Опиши совместимость. Обязательно:\n"
            f"1. В чём сила этой пары\n2. Главный источник конфликтов\n"
            f"3. Практический совет\nОбъём: 90-110 слов."
        )
    else:
        prompt = (
            f"Compatibility ({req.compat_type}): {s1} and {s2}. Score: {req.score}%.\n"
            f"Describe compatibility:\n1. Pair's strength\n2. Main conflict source\n"
            f"3. Practical tip\n90-110 words."
        )

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "compat_interpret", 5, 50)
    msgs = [{"role": "system", "content": sys + lang_enforce}, {"role": "user", "content": prompt}]

    return StreamingResponse(safe_groq_stream(msgs, max_tokens=300, lang=req.lang),
                             media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
