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
"""
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
from app.data.destiny_matrix import POINT_IDS, arcana_name, build_matrix, calculate
from app.data.karmic_tail import KARMIC_TAIL, build_karmic_tail, calculate_tail, tail_code
from app.models.user import User, UserProfile

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
