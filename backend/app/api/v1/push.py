import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.push import send_push_sync
from app.models.user import User, UserProfile

router = APIRouter()


class SubscribeRequest(BaseModel):
    subscription: dict


@router.post("/push/subscribe")
async def push_subscribe(
    req: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        session.add(profile)
    profile.push_subscription = json.dumps(req.subscription)
    session.add(profile)
    await session.commit()
    return {"status": "ok"}


@router.delete("/push/unsubscribe")
async def push_unsubscribe(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.first()
    if profile:
        profile.push_subscription = None
        session.add(profile)
        await session.commit()
    return {"status": "ok"}


@router.post("/push/test")
async def push_test(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.first()
    if not profile or not profile.push_subscription:
        return {"status": "no_subscription"}
    sub = json.loads(profile.push_subscription)
    r = send_push_sync(sub, "Mystral", "Push-уведомления работают!", "/")
    return {"status": r or "error"}
