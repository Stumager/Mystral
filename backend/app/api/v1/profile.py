import hmac
import os
from datetime import date, datetime, time
from typing import Optional
from zoneinfo import available_timezones

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import AuthProvider, User, UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


async def _require_internal_token(x_internal_token: str = Header("")):
    if not settings.admin_token or not hmac.compare_digest(x_internal_token, settings.admin_token):
        raise HTTPException(status_code=403, detail="Forbidden")

VALID_TIMEZONES = available_timezones()


class ProfileUpdate(BaseModel):
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_time_known: Optional[bool] = None
    birth_city: Optional[str] = None
    birth_name: Optional[str] = None
    full_name: Optional[str] = None
    lang: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    timezone: Optional[str] = None


class ToggleNotifRequest(BaseModel):
    telegram_id: str


def _completion(profile: UserProfile) -> int:
    fields = [profile.birth_date, profile.birth_time, profile.birth_city, profile.birth_name_enc]
    return round(sum(1 for f in fields if f is not None) / 4 * 100)


def _serialize(profile: UserProfile, user: Optional["User"] = None) -> dict:
    result = {
        "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
        "birth_time": profile.birth_time.strftime("%H:%M") if profile.birth_time else None,
        "birth_time_known": profile.birth_time_known,
        "birth_city": profile.birth_city,
        "birth_name": profile.birth_name_enc,
        "full_name": profile.full_name,
        "completion_percent": _completion(profile),
        "notifications_enabled": profile.notifications_enabled,
        "timezone": profile.timezone,
        "subscription_expires_at": None,
        "days_left": None,
    }
    if user and user.subscription_tier == "pro" and user.subscription_expires_at:
        result["subscription_expires_at"] = user.subscription_expires_at.isoformat()
        delta = (user.subscription_expires_at - datetime.utcnow()).days
        result["days_left"] = max(0, delta)
    return result


async def _get_or_create(user_id, session: AsyncSession) -> UserProfile:
    result = await session.exec(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    return profile


@router.get("")
async def get_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    profile = await _get_or_create(current_user.id, session)
    return _serialize(profile, current_user)


@router.put("")
async def update_profile(
    req: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    profile = await _get_or_create(current_user.id, session)

    if req.birth_date is not None:
        try:
            profile.birth_date = date.fromisoformat(req.birth_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid birth_date, use YYYY-MM-DD")

    if req.birth_time is not None:
        try:
            h, m = req.birth_time.split(":")
            profile.birth_time = time(int(h), int(m))
            profile.birth_time_known = True
        except (ValueError, AttributeError):
            raise HTTPException(status_code=422, detail="Invalid birth_time, use HH:MM")

    if req.birth_time_known is not None:
        profile.birth_time_known = req.birth_time_known

    if req.birth_city is not None:
        profile.birth_city = req.birth_city

    if req.birth_name is not None:
        profile.birth_name_enc = req.birth_name

    if req.full_name is not None:
        profile.full_name = req.full_name

    invalidate_num_cache = (req.birth_date is not None or req.full_name is not None)

    if req.lang is not None:
        current_user.lang = req.lang
        session.add(current_user)

    if req.notifications_enabled is not None:
        profile.notifications_enabled = req.notifications_enabled

    if req.timezone is not None:
        if req.timezone not in VALID_TIMEZONES:
            raise HTTPException(status_code=400, detail="Invalid timezone")
        profile.timezone = req.timezone

    await session.commit()
    await session.refresh(profile)

    if invalidate_num_cache:
        try:
            r = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
            await r.delete(f"numerology:{current_user.id}")
            await r.close()
        except Exception:
            pass

    return _serialize(profile, current_user)


@router.post("/toggle-notifications", dependencies=[Depends(_require_internal_token)])
async def toggle_notifications(
    req: ToggleNotifRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "telegram",
            AuthProvider.provider_id == req.telegram_id,
        )
    )
    provider = result.first()
    if not provider:
        raise HTTPException(status_code=404, detail="User not found")

    profile = await _get_or_create(provider.user_id, session)
    profile.notifications_enabled = not profile.notifications_enabled
    await session.commit()
    await session.refresh(profile)
    return {"notifications_enabled": profile.notifications_enabled}
