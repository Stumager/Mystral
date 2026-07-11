import secrets
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.auth import _check_ip_rate, _get_ip
from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import ReferralLog, User, UserProfile

router = APIRouter()


def _gen_ref_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


async def _ensure_ref_code(user: User, session: AsyncSession) -> str:
    if not user.ref_code:
        code = _gen_ref_code()
        while (await session.exec(select(User).where(User.ref_code == code))).first():
            code = _gen_ref_code()
        user.ref_code = code
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user.ref_code


def _extend_pro(user: User, days: int) -> None:
    now = datetime.utcnow()
    base = user.subscription_expires_at if user.subscription_expires_at and user.subscription_expires_at > now else now
    user.subscription_tier = "pro"
    user.subscription_expires_at = base + timedelta(days=days)


@router.get("/referrals/my")
async def my_referrals(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    code = await _ensure_ref_code(current_user, session)

    count_q = await session.exec(
        select(func.count()).select_from(ReferralLog).where(ReferralLog.referrer_id == current_user.id)
    )
    total = count_q.one()

    days_q = await session.exec(
        select(func.coalesce(func.sum(ReferralLog.bonus_days), 0)).where(ReferralLog.referrer_id == current_user.id)
    )
    total_days = days_q.one()

    logs = (await session.exec(
        select(ReferralLog).where(ReferralLog.referrer_id == current_user.id).order_by(ReferralLog.created_at.desc()).limit(20)
    )).all()

    referrals = []
    for log in logs:
        referred = await session.get(User, log.referred_id)
        name = (referred.display_name or "?")[:2] + "***" if referred else "?"
        profile_q = await session.exec(select(UserProfile).where(UserProfile.user_id == log.referred_id))
        profile = profile_q.first()
        zodiac = None
        if profile and profile.birth_date:
            from app.services.horoscope import zodiac_from_date
            zodiac = zodiac_from_date(profile.birth_date)
        referrals.append({
            "name": name,
            "zodiac_sign": zodiac,
            "bonus_days": log.bonus_days,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })

    return {
        "ref_code": code,
        "ref_url": f"https://mystral.space/ref/{code}",
        "total_referrals": total,
        "total_bonus_days": int(total_days),
        "referrals": referrals,
    }


class ApplyRefRequest(BaseModel):
    ref_code: str


@router.post("/referrals/apply")
async def apply_referral(
    req: ApplyRefRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await _check_ip_rate(_get_ip(request), "referral_apply", 5, 3600)

    if current_user.referred_by:
        raise HTTPException(400, "Реферальный код уже применён")

    # Telegram-native accounts have no email at all (auth_telegram() never sets
    # one) and email_verified defaults to False forever for them — only email
    # registrations need to prove a real inbox before a bonus counts.
    if current_user.email and not current_user.email_verified:
        raise HTTPException(400, "Подтвердите email перед применением реферального кода")

    result = await session.exec(select(User).where(User.ref_code == req.ref_code))
    referrer = result.first()
    if not referrer:
        raise HTTPException(404, "Код не найден")
    if referrer.id == current_user.id:
        raise HTTPException(400, "Нельзя применить свой код")

    _extend_pro(current_user, 3)
    current_user.referred_by = referrer.id
    session.add(current_user)

    _extend_pro(referrer, 7)
    referrer.ref_bonus_days_given = (referrer.ref_bonus_days_given or 0) + 7
    session.add(referrer)

    log = ReferralLog(referrer_id=referrer.id, referred_id=current_user.id, bonus_days=7)
    session.add(log)

    await session.commit()
    return {"status": "ok", "bonus_days": 3}


@router.get("/referrals/stats")
async def referral_stats(session: AsyncSession = Depends(get_session)):
    count_q = await session.exec(select(func.count()).select_from(ReferralLog))
    return {"total_referrals": count_q.one()}
