from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.models.user import AuthProvider, User, UserProfile

router = APIRouter()


async def is_admin(x_admin_token: str = Header("")):
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(403, "Forbidden")


@router.get("/admin/stats", dependencies=[Depends(is_admin)])
async def admin_stats(session: AsyncSession = Depends(get_session)):
    now = datetime.utcnow()

    total = (await session.exec(select(func.count()).select_from(User))).one()
    pro = (await session.exec(
        select(func.count()).select_from(User).where(User.subscription_tier == "pro")
    )).one()
    new_7 = (await session.exec(
        select(func.count()).select_from(User).where(User.created_at >= now - timedelta(days=7))
    )).one()
    new_30 = (await session.exec(
        select(func.count()).select_from(User).where(User.created_at >= now - timedelta(days=30))
    )).one()

    return {"total_users": total, "pro_users": pro, "new_7days": new_7, "new_30days": new_30}


@router.get("/admin/users", dependencies=[Depends(is_admin)])
async def admin_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    session: AsyncSession = Depends(get_session),
):
    base = (
        select(User, AuthProvider)
        .outerjoin(AuthProvider, AuthProvider.user_id == User.id)
    )
    count_q = select(func.count(func.distinct(User.id))).select_from(User)

    if search:
        like = f"%{search}%"
        base = base.outerjoin(AuthProvider, AuthProvider.user_id == User.id)
        base = (
            select(User, AuthProvider)
            .outerjoin(AuthProvider, AuthProvider.user_id == User.id)
            .where(
                (User.email.ilike(like)) |
                (AuthProvider.provider_id.ilike(like))
            )
        )
        count_q = (
            select(func.count(func.distinct(User.id)))
            .select_from(User)
            .outerjoin(AuthProvider, AuthProvider.user_id == User.id)
            .where(
                (User.email.ilike(like)) |
                (AuthProvider.provider_id.ilike(like))
            )
        )

    total = (await session.exec(count_q)).one()
    pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit

    rows = (await session.exec(
        base.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )).all()

    seen: set[str] = set()
    users = []
    for row in rows:
        if isinstance(row, tuple):
            u, ap = row
        else:
            u = row
            ap = None
        uid = str(u.id)
        if uid in seen:
            continue
        seen.add(uid)

        tg_id = None
        tg_user = None
        if ap and ap.provider == "telegram":
            tg_id = ap.provider_id
        else:
            tg_res = await session.exec(
                select(AuthProvider).where(AuthProvider.user_id == u.id, AuthProvider.provider == "telegram")
            )
            tg_ap = tg_res.first()
            if tg_ap:
                tg_id = tg_ap.provider_id

        users.append({
            "id": uid,
            "email": u.email,
            "display_name": u.display_name,
            "telegram_id": tg_id,
            "tier": u.subscription_tier,
            "subscription_expires_at": u.subscription_expires_at.isoformat() if u.subscription_expires_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })

    return {"users": users, "total": total, "page": page, "pages": pages}


class GrantProRequest(BaseModel):
    days: int = 30


@router.post("/admin/users/{user_id}/grant-pro", dependencies=[Depends(is_admin)])
async def grant_pro(user_id: UUID, req: GrantProRequest, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.subscription_tier = "pro"
    user.subscription_expires_at = datetime.utcnow() + timedelta(days=req.days)
    session.add(user)
    await session.commit()
    return {"ok": True}


@router.post("/admin/users/{user_id}/revoke-pro", dependencies=[Depends(is_admin)])
async def revoke_pro(user_id: UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.subscription_tier = "free"
    user.subscription_expires_at = None
    session.add(user)
    await session.commit()
    return {"ok": True}


@router.delete("/admin/users/{user_id}", dependencies=[Depends(is_admin)])
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    await session.execute(text("DELETE FROM auth_providers WHERE user_id = :uid"), {"uid": user_id})
    await session.execute(text("DELETE FROM user_profiles WHERE user_id = :uid"), {"uid": user_id})
    await session.execute(text("DELETE FROM tarot_readings WHERE user_id = :uid"), {"uid": user_id})
    await session.execute(text("DELETE FROM rune_readings WHERE user_id = :uid"), {"uid": user_id})
    await session.execute(text("DELETE FROM user_partners WHERE user_id = :uid"), {"uid": user_id})
    await session.delete(user)
    await session.commit()
    return {"ok": True}
