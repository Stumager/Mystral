"""TZ-101: Матрица судьбы — base version.

Access model (confirmed with the product owner before implementation): the
matrix itself — every arcana number, name and keyword pair — is free for any
authenticated user, exactly like the natal wheel; every generated reading is
Pro. So GET /matrix carries no tier gate and POST /matrix/interpret rejects
free users outright.

The matrix is a pure function of the birth date, so unlike tarot/runes there
is no reading row to persist and nothing to cache against a reading_id — the
same date always rebuilds the same nine points.

TZ-114 (Кармический хвост, "Послание кармы") reuses these same nine points —
no new user input — but its own access model is different, confirmed
separately with the product owner: unlike the base matrix, it has no free
sample at all. Both GET /matrix/karmic-tail and POST
/matrix/karmic-tail/interpret reject free users.

TZ-115 (Денежная линия, "Послание денег") — third module on the same nine
points, same access model as TZ-114: no free sample, both GET
/matrix/money-line and POST /matrix/money-line/interpret reject free users.

TZ-116 (Детская матрица, "Послание детства") — fourth module, same nine
points reinterpreted for a parent reading about their child. Access model
is different again, confirmed with the product owner: unlike TZ-114/115,
there IS a free sample — the "talents" point (the child's main-talent
hook) is visible to free users, the other eight points and the AI reading
are Pro. Mirrors natal.py's "one free section, rest gated" shape rather
than TZ-114/115's all-or-nothing gate.
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.groq_client import safe_groq_stream
from app.core.limiter import check_rate_limit
from app.core.prompts import lang_enforce, system_prompt
from app.data.childrens_matrix import FREE_POINT_ID, build_children_matrix
from app.data.destiny_matrix import POINT_IDS, arcana_name, build_matrix, calculate
from app.data.karmic_tail import KARMIC_TAIL, build_karmic_tail, calculate_tail, tail_code
from app.data.money_line import MONEY_LINE_POSITIONS, build_money_line, calculate_money_line
from app.models.user import User, UserChild, UserProfile

router = APIRouter()


# What each point stands for, phrased for the model rather than for the UI —
# the user-facing labels live in the frontend locale files.
POINT_PROMPT_RU = {
    "personality": "Личность — характер и первое впечатление, каким человека считывают окружающие",
    "talents": "Таланты — способности, данные от рождения",
    "ancestry": "Родовые программы — то, что приходит по роду и работает фоном",
    "realization": "Реализация в социуме — как человек проявляется во внешнем мире и в деле",
    "core": "Точка опоры — центр матрицы, зона комфорта, главные страхи и главные радости",
    "father_gift": "Дар отцовского рода — ресурс, который даёт мужская линия",
    "mother_gift": "Дар материнского рода — ресурс, который даёт женская линия",
    "father_task": "Задача отцовского рода — то, что мужская линия просит проработать",
    "mother_task": "Задача материнского рода — то, что женская линия просит проработать",
}

POINT_PROMPT_EN = {
    "personality": "Personality — character and first impression, how others read this person",
    "talents": "Talents — abilities given at birth",
    "ancestry": "Ancestral programs — what comes down the family line and runs in the background",
    "realization": "Social realization — how this person shows up in the outer world and in their work",
    "core": "Inner core — the centre of the matrix: comfort zone, deepest fears and deepest joys",
    "father_gift": "Father's line gift — the resource the paternal line provides",
    "mother_gift": "Mother's line gift — the resource the maternal line provides",
    "father_task": "Father's line task — what the paternal line asks to be worked through",
    "mother_task": "Mother's line task — what the maternal line asks to be worked through",
}


class InterpretRequest(BaseModel):
    point: str
    lang: str = "ru"


async def _birth_date(session: AsyncSession, user: User):
    result = await session.exec(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.first()
    if not profile or not profile.birth_date:
        raise HTTPException(400, "birth_date required")
    return profile.birth_date


@router.get("/matrix")
async def matrix(
    lang: str = "ru",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    bd = await _birth_date(session, current_user)
    return {"birth_date": bd.isoformat(), **build_matrix(bd, lang)}


@router.post("/matrix/interpret")
async def interpret(
    req: InterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")
    if req.point not in POINT_IDS:
        raise HTTPException(422, "unknown point")

    bd = await _birth_date(session, current_user)

    # TZ-089/091/097: the pooled connection this request holds via
    # Depends(get_session) would otherwise stay checked out for the whole SSE
    # stream below, because dependency cleanup doesn't run until the response
    # body is fully sent. Everything from the DB is already read by here.
    await session.close()

    ru = req.lang == "ru"
    values = calculate(bd)
    n = values[req.point]
    labels = POINT_PROMPT_RU if ru else POINT_PROMPT_EN

    # The whole octagram goes into the prompt, not just the one point — a
    # point reads differently depending on what surrounds it, and this is the
    # difference between a generic arcana description and an actual matrix
    # reading.
    full = ", ".join(
        f"{labels[pid]}: аркан {values[pid]} ({arcana_name(values[pid], req.lang)})" if ru
        else f"{labels[pid]}: arcana {values[pid]} ({arcana_name(values[pid], req.lang)})"
        for pid in POINT_IDS
    )

    if ru:
        prompt = (
            f"Матрица судьбы человека целиком: {full}.\n\n"
            f"Разбери одну точку — «{labels[req.point]}», аркан {n} "
            f"({arcana_name(n, req.lang)}).\n"
            f"Структура ответа:\n"
            f"1. Что эта энергия даёт человеку, когда проявлена в плюсе\n"
            f"2. Как она же выглядит в теневом, непроработанном виде\n"
            f"3. Один конкретный шаг, чтобы развернуть её в плюс\n"
            f"Учитывай соседние точки матрицы, если они усиливают или "
            f"противоречат этой. Обращайся на «ты». 150-250 слов, без воды."
        )
    else:
        prompt = (
            f"The person's full destiny matrix: {full}.\n\n"
            f"Interpret one point — \"{labels[req.point]}\", arcana {n} "
            f"({arcana_name(n, req.lang)}).\n"
            f"Structure:\n"
            f"1. What this energy gives when it's expressed at its best\n"
            f"2. How the same energy looks in its shadow, unworked form\n"
            f"3. One concrete step to turn it toward the light side\n"
            f"Take the neighbouring points into account where they reinforce "
            f"or contradict this one. 150-250 words, no filler."
        )
    prompt += lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "matrix_interpret", 0, 20)
    msgs = [
        {"role": "system", "content": system_prompt(req.lang) + lang_enforce(req.lang)},
        {"role": "user", "content": prompt},
    ]
    return StreamingResponse(
        safe_groq_stream(msgs, max_tokens=900, lang=req.lang),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# What each money-line position stands for, phrased for the model — mirrors
# POINT_PROMPT_RU/EN above. "entry" is deliberately the same value as the
# karmic tail's first digit (see money_line.py's docstring) — the prompt
# says so explicitly rather than leaving the model to notice on its own.
MONEY_POSITION_PROMPT_RU = {
    "entry": "Вход в денежный поток — что притягивает деньги в сторону человека",
    "source": "Источник дохода — за какие качества и сферы деятельности платят",
    "block": "Блок денежного потока — что перекрывает деньги, когда энергия не проработана",
}

MONEY_POSITION_PROMPT_EN = {
    "entry": "Entry into the money flow — what draws money toward this person",
    "source": "Income source — which qualities and spheres of activity get paid",
    "block": "Money-flow block — what shuts money off when this energy is unworked",
}


class KarmicTailInterpretRequest(BaseModel):
    lang: str = "ru"


@router.get("/matrix/karmic-tail")
async def karmic_tail(
    lang: str = "ru",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """TZ-114: unlike the base matrix, the karmic tail carries no free
    sample — the whole feature (calculation and reading alike) is Pro-only,
    confirmed with the product owner."""
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")
    bd = await _birth_date(session, current_user)
    return {"birth_date": bd.isoformat(), **build_karmic_tail(bd, lang)}


@router.post("/matrix/karmic-tail/interpret")
async def karmic_tail_interpret(
    req: KarmicTailInterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    bd = await _birth_date(session, current_user)

    # Same TZ-089/091/097 fix as /matrix/interpret above.
    await session.close()

    ru = req.lang == "ru"
    values = calculate(bd)
    tail = calculate_tail(values)
    code = tail_code(tail)
    entry = KARMIC_TAIL[code]

    if ru:
        prompt = (
            f"Кармический хвост человека — комбинация {code} «{entry['name_ru']}».\n"
            f"Рабочее описание архетипа: {entry['essence_ru']}.\n"
            f"Направление проработки: {entry['task_ru']}.\n\n"
            f"Напиши персональное послание кармического хвоста для этого человека.\n"
            f"Структура ответа:\n"
            f"1. Какой незавершённый сюжет прошлого воплощения стоит за этой комбинацией\n"
            f"2. Как он обычно проявляется в нынешней жизни — в отношениях, деле или теле\n"
            f"3. Один конкретный шаг для проработки в ближайшее время\n"
            f"Обращайся на «ты». 150-250 слов, без воды."
        )
    else:
        prompt = (
            f"This person's karmic tail is combination {code} \"{entry['name_en']}\".\n"
            f"Working description of the archetype: {entry['essence_en']}.\n"
            f"Direction for the work ahead: {entry['task_en']}.\n\n"
            f"Write a personal karmic-tail reading for this person.\n"
            f"Structure:\n"
            f"1. What unfinished story from a past life sits behind this combination\n"
            f"2. How it typically shows up in this life — in relationships, work, or the body\n"
            f"3. One concrete step to work on soon\n"
            f"150-250 words, no filler."
        )
    prompt += lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "karmic_tail_interpret", 0, 20)
    msgs = [
        {"role": "system", "content": system_prompt(req.lang) + lang_enforce(req.lang)},
        {"role": "user", "content": prompt},
    ]
    return StreamingResponse(
        safe_groq_stream(msgs, max_tokens=900, lang=req.lang),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class MoneyLineInterpretRequest(BaseModel):
    lang: str = "ru"


@router.get("/matrix/money-line")
async def money_line(
    lang: str = "ru",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """TZ-115: same access model as the karmic tail — no free sample."""
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")
    bd = await _birth_date(session, current_user)
    return {"birth_date": bd.isoformat(), **build_money_line(bd, lang)}


@router.post("/matrix/money-line/interpret")
async def money_line_interpret(
    req: MoneyLineInterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")

    bd = await _birth_date(session, current_user)

    # Same TZ-089/091/097 fix as the other streaming endpoints above.
    await session.close()

    ru = req.lang == "ru"
    points = calculate(bd)
    values = calculate_money_line(points)
    labels = MONEY_POSITION_PROMPT_RU if ru else MONEY_POSITION_PROMPT_EN

    full = ", ".join(
        f"{labels[pos]}: аркан {values[pos]} ({arcana_name(values[pos], req.lang)})" if ru
        else f"{labels[pos]}: arcana {values[pos]} ({arcana_name(values[pos], req.lang)})"
        for pos in MONEY_LINE_POSITIONS
    )

    if ru:
        prompt = (
            f"Денежная линия человека целиком: {full}.\n\n"
            f"Напиши персональное послание денежной линии для этого человека.\n"
            f"Структура ответа:\n"
            f"1. Что притягивает деньги в сторону человека (точка входа)\n"
            f"2. За какие качества и сферы деятельности будут платить (источник дохода)\n"
            f"3. Что перекрывает поток, если эта энергия не проработана, и один "
            f"конкретный шаг для проработки (блок)\n"
            f"Обращайся на «ты». 150-250 слов, без воды."
        )
    else:
        prompt = (
            f"This person's full money line: {full}.\n\n"
            f"Write a personal money-line reading for this person.\n"
            f"Structure:\n"
            f"1. What draws money toward this person (the entry point)\n"
            f"2. Which qualities and spheres of activity will get paid (the income source)\n"
            f"3. What shuts the flow off when this energy is unworked, and one "
            f"concrete step to work on it (the block)\n"
            f"150-250 words, no filler."
        )
    prompt += lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "money_line_interpret", 0, 20)
    msgs = [
        {"role": "system", "content": system_prompt(req.lang) + lang_enforce(req.lang)},
        {"role": "user", "content": prompt},
    ]
    return StreamingResponse(
        safe_groq_stream(msgs, max_tokens=900, lang=req.lang),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---- Child CRUD (TZ-116) — mirrors compatibility.py's partner CRUD ----

def _parse_child_id(child_id: str) -> UUID:
    try:
        return UUID(child_id)
    except ValueError:
        raise HTTPException(422, "Invalid child_id")


async def _get_owned_child(session: AsyncSession, user: User, child_id: str) -> UserChild:
    child = await session.get(UserChild, _parse_child_id(child_id))
    if not child or child.user_id != user.id:
        raise HTTPException(404, "Child not found")
    return child


class ChildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    birth_date: str


@router.get("/children")
async def list_children(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(UserChild).where(UserChild.user_id == current_user.id)
        .order_by(UserChild.created_at.desc())
    )
    return [
        {"id": str(c.id), "name": c.label, "birth_date": c.birth_date.isoformat()}
        for c in result.all()
    ]


@router.post("/children")
async def create_child(
    req: ChildCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    bd = date.fromisoformat(req.birth_date)
    child = UserChild(user_id=current_user.id, label=req.name, birth_date=bd)
    session.add(child)
    await session.commit()
    await session.refresh(child)
    return {"id": str(child.id)}


@router.delete("/children/{child_id}")
async def delete_child(
    child_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    child = await _get_owned_child(session, current_user, child_id)
    await session.delete(child)
    await session.commit()


# ---- Children's Matrix (TZ-116) ----

# Phrased for a parent reading about their child, not for the child reading
# about themselves — see the module docstring for the access model.
CHILD_POINT_PROMPT_RU = {
    "personality": "Личность ребёнка — как его считывают окружающие, первое впечатление",
    "talents": "Врождённые таланты ребёнка — способности, с которыми он пришёл в этот мир",
    "ancestry": "Родовые программы — то, что ребёнок несёт по роду фоном",
    "realization": "Проявление в мире — как ребёнок будет раскрываться в учёбе, деле, окружении",
    "core": "Точка опоры ребёнка — что даёт ему чувство безопасности и радости",
    "father_gift": "Дар отцовского рода для ребёнка",
    "mother_gift": "Дар материнского рода для ребёнка",
    "father_task": "Задача отцовской линии в жизни ребёнка",
    "mother_task": "Задача материнской линии в жизни ребёнка",
}

CHILD_POINT_PROMPT_EN = {
    "personality": "The child's personality — how others read them, first impression",
    "talents": "The child's innate talents — abilities they were born with",
    "ancestry": "Ancestral programs — what the child carries from the family line in the background",
    "realization": "How the child shows up in the world — school, activities, surroundings",
    "core": "The child's inner core — what gives them a sense of safety and joy",
    "father_gift": "The father's line gift for this child",
    "mother_gift": "The mother's line gift for this child",
    "father_task": "What the father's line asks to be worked through in this child's life",
    "mother_task": "What the mother's line asks to be worked through in this child's life",
}


class ChildInterpretRequest(BaseModel):
    point: str
    lang: str = "ru"


@router.get("/matrix/child/{child_id}")
async def matrix_child(
    child_id: str,
    lang: str = "ru",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """TZ-116: unlike TZ-114/115's all-or-nothing gate, this has a free
    sample — the "talents" point — confirmed with the product owner as a
    stronger conversion hook than a fully paywalled first screen. The other
    eight points come back locked for free users."""
    child = await _get_owned_child(session, current_user, child_id)
    result = build_children_matrix(child.birth_date, lang)
    free = current_user.subscription_tier == "free"
    for p in result["points"]:
        if free and p["id"] != FREE_POINT_ID:
            p["arcana"] = None
            p["arcana_name"] = None
            p["strength"] = None
            p["support"] = None
            p["locked"] = True
        else:
            p["locked"] = False
    return {
        "child": {"id": str(child.id), "name": child.label, "birth_date": child.birth_date.isoformat()},
        **result,
    }


@router.post("/matrix/child/{child_id}/interpret")
async def matrix_child_interpret(
    child_id: str,
    req: ChildInterpretRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.subscription_tier == "free":
        raise HTTPException(402, "FREE_LIMIT_REACHED")
    if req.point not in POINT_IDS:
        raise HTTPException(422, "unknown point")

    child = await _get_owned_child(session, current_user, child_id)

    # Same TZ-089/091/097 fix as the other streaming endpoints above.
    await session.close()

    ru = req.lang == "ru"
    values = calculate(child.birth_date)
    n = values[req.point]
    labels = CHILD_POINT_PROMPT_RU if ru else CHILD_POINT_PROMPT_EN

    full = ", ".join(
        f"{labels[pid]}: аркан {values[pid]} ({arcana_name(values[pid], req.lang)})" if ru
        else f"{labels[pid]}: arcana {values[pid]} ({arcana_name(values[pid], req.lang)})"
        for pid in POINT_IDS
    )

    if ru:
        prompt = (
            f"Матрица ребёнка по имени {child.label} целиком: {full}.\n\n"
            f"Разбери одну точку — «{labels[req.point]}», аркан {n} "
            f"({arcana_name(n, req.lang)}) — для родителя, о ребёнке.\n"
            f"Структура ответа:\n"
            f"1. Какая природная склонность стоит за этой энергией у ребёнка\n"
            f"2. Как родитель может это поддержать и направить, а не ограничить\n"
            f"3. Один конкретный, посильный ребёнку шаг или совместное действие\n"
            f"Обращайся к родителю на «ты». Не давай категоричных ярлыков вроде "
            f"«ему не дано» или «он не способен» — только развивающую рамку. "
            f"150-250 слов, без воды."
        )
    else:
        prompt = (
            f"The full matrix of a child named {child.label}: {full}.\n\n"
            f"Interpret one point — \"{labels[req.point]}\", arcana {n} "
            f"({arcana_name(n, req.lang)}) — for a parent, about their child.\n"
            f"Structure:\n"
            f"1. What natural inclination sits behind this energy in the child\n"
            f"2. How a parent can support and direct it, not limit it\n"
            f"3. One concrete, age-appropriate step or shared activity\n"
            f"Do not hand down flat labels like \"not cut out for it\" or \"can't do "
            f"it\" — a developmental frame only. 150-250 words, no filler."
        )
    prompt += lang_enforce(req.lang)

    await check_rate_limit(str(current_user.id), current_user.subscription_tier, "children_matrix_interpret", 0, 20)
    msgs = [
        {"role": "system", "content": system_prompt(req.lang) + lang_enforce(req.lang)},
        {"role": "user", "content": prompt},
    ]
    return StreamingResponse(
        safe_groq_stream(msgs, max_tokens=900, lang=req.lang),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
