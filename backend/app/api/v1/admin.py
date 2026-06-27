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
from app.models.user import AuthProvider, Review, User

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
    q = select(User)
    count_q = select(func.count()).select_from(User)

    if search:
        like = f"%{search}%"
        sub = select(AuthProvider.user_id).where(AuthProvider.provider_id.ilike(like))
        filt = (User.email.ilike(like)) | (User.id.in_(sub))
        q = q.where(filt)
        count_q = count_q.where(filt)

    total = (await session.exec(count_q)).one()
    pages_count = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit

    user_rows = (await session.exec(
        q.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )).all()

    result = []
    for u in user_rows:
        tg_ap = (await session.exec(
            select(AuthProvider).where(AuthProvider.user_id == u.id, AuthProvider.provider == "telegram")
        )).first()

        result.append({
            "id": str(u.id),
            "email": u.email,
            "display_name": u.display_name,
            "telegram_id": tg_ap.provider_id if tg_ap else None,
            "tier": u.subscription_tier,
            "subscription_expires_at": u.subscription_expires_at.isoformat() if u.subscription_expires_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })

    return {"users": result, "total": total, "page": page, "pages": pages_count}


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
    for table in ["auth_providers", "user_profiles", "tarot_readings", "rune_readings", "user_partners", "reviews"]:
        await session.execute(text(f"DELETE FROM {table} WHERE user_id = :uid"), {"uid": user_id})
    await session.delete(user)
    await session.commit()
    return {"ok": True}


@router.get("/admin/reviews", dependencies=[Depends(is_admin)])
async def admin_reviews(
    published: Optional[bool] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    q = select(Review)
    if published is not None:
        q = q.where(Review.is_published == published)
    rows = (await session.exec(q.order_by(Review.created_at.desc()))).all()

    result = []
    for r in rows:
        user = await session.get(User, r.user_id)
        result.append({
            "id": str(r.id),
            "user_name": user.display_name if user else "?",
            "user_email": user.email if user else None,
            "rating": r.rating,
            "text": r.text,
            "is_published": r.is_published,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return result


@router.post("/admin/reviews/{review_id}/publish", dependencies=[Depends(is_admin)])
async def publish_review(review_id: UUID, session: AsyncSession = Depends(get_session)):
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    review.is_published = True
    session.add(review)
    await session.commit()
    return {"ok": True}


@router.delete("/admin/reviews/{review_id}", dependencies=[Depends(is_admin)])
async def delete_review(review_id: UUID, session: AsyncSession = Depends(get_session)):
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    await session.delete(review)
    await session.commit()
    return {"ok": True}
