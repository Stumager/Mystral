import hmac
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.payments import stars_issue_refund, yukassa_issue_refund
from app.core.config import settings
from app.core.database import get_session
from app.core.email import send_refund_decision_email
from app.models.user import AuthProvider, Payment, ReferralLog, RefundRequest, Review, User

router = APIRouter()
logger = logging.getLogger(__name__)


async def is_admin(request: Request, x_admin_token: str = Header("")):
    # 30 req/min per IP across all admin endpoints, and constant-time token compare
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[-1].strip() if forwarded else (request.client.host if request.client else "unknown")
    r = aioredis.from_url(settings.redis_url)
    try:
        key = f"admin_rl:{ip}"
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, 60)
        if count > 30:
            raise HTTPException(429, "Too many requests")
    finally:
        await r.close()

    if not settings.admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
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
    # refund_requests before payments (FK on payment_id), both before the rest —
    # Postgres enforces these FKs (SQLite in tests doesn't by default, which is
    # how this list went stale without a test catching it).
    # .hex (no hyphens) matches how SQLite stores UUID columns; Postgres's uuid
    # type accepts that form too, so this works against both without relying on
    # the ORM's type decorator (which text() bypasses).
    for table in ["refund_requests", "payments", "auth_providers", "user_profiles", "tarot_readings", "rune_readings", "user_partners", "reviews"]:
        await session.execute(text(f"DELETE FROM {table} WHERE user_id = :uid"), {"uid": user_id.hex})
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


@router.get("/admin/referrals/stats", dependencies=[Depends(is_admin)])
async def admin_referral_stats(session: AsyncSession = Depends(get_session)):
    total_q = await session.exec(select(func.count()).select_from(ReferralLog))
    total = total_q.one()

    days_q = await session.exec(select(func.coalesce(func.sum(ReferralLog.bonus_days), 0)).select_from(ReferralLog))
    total_days = days_q.one()

    top_q = (await session.exec(
        select(User.id, User.display_name, User.email, User.ref_code, User.ref_bonus_days_given)
        .where(User.ref_bonus_days_given > 0)
        .order_by(User.ref_bonus_days_given.desc())
        .limit(10)
    )).all()

    top = []
    for row in top_q:
        uid, name, email, code, days = row
        cnt_q = await session.exec(select(func.count()).select_from(ReferralLog).where(ReferralLog.referrer_id == uid))
        top.append({"name": name, "email": email, "ref_code": code, "referral_count": cnt_q.one(), "bonus_days": days or 0})

    recent_q = (await session.exec(
        select(ReferralLog).order_by(ReferralLog.created_at.desc()).limit(20)
    )).all()

    recent = []
    for log in recent_q:
        referrer = await session.get(User, log.referrer_id)
        referred = await session.get(User, log.referred_id)
        recent.append({
            "referrer_name": referrer.display_name if referrer else "?",
            "referred_name": referred.display_name if referred else "?",
            "bonus_days": log.bonus_days,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })

    return {"total_referrals": total, "total_bonus_days_given": int(total_days), "top_referrers": top, "recent": recent}


async def _serialize_refund_request(req: RefundRequest, session: AsyncSession) -> dict:
    payment = await session.get(Payment, req.payment_id)
    user = await session.get(User, req.user_id)
    tg_ap = None
    if user:
        tg_result = await session.exec(
            select(AuthProvider).where(AuthProvider.user_id == user.id, AuthProvider.provider == "telegram")
        )
        tg_ap = tg_result.first()

    return {
        "id": str(req.id),
        "status": req.status,
        "reason": req.reason,
        "admin_comment": req.admin_comment,
        "error_detail": req.error_detail,
        "created_at": req.created_at.isoformat() if req.created_at else None,
        "resolved_at": req.resolved_at.isoformat() if req.resolved_at else None,
        "resolved_by": req.resolved_by,
        "user": {
            "id": str(user.id) if user else None,
            "email": user.email if user else None,
            "display_name": user.display_name if user else None,
            "telegram_id": tg_ap.provider_id if tg_ap else None,
        },
        "payment": {
            "provider": payment.provider,
            "product": payment.product,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        } if payment else None,
    }


@router.get("/admin/refunds", dependencies=[Depends(is_admin)])
async def admin_refunds(session: AsyncSession = Depends(get_session)):
    rows = (await session.exec(select(RefundRequest).order_by(RefundRequest.created_at.desc()))).all()
    serialized = [await _serialize_refund_request(r, session) for r in rows]
    return {
        "pending": [r for r in serialized if r["status"] == "pending"],
        "resolved": [r for r in serialized if r["status"] != "pending"],
    }


@router.post("/admin/refunds/{request_id}/approve", dependencies=[Depends(is_admin)])
async def approve_refund(request_id: UUID, session: AsyncSession = Depends(get_session)):
    """TZ-065: approving here means actually calling the provider (YuKassa
    /v3/refunds or Telegram refundStarPayment) — this is the only place in the
    codebase that initiates a real refund. Pro revocation itself is NOT done
    here: it happens automatically via the existing refund.succeeded webhook
    (TZ-061) / refunded_payment bot handler (TZ-064) once the provider confirms,
    so we don't duplicate that idempotent logic a second time."""
    req = await session.get(RefundRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Refund request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already resolved (status={req.status})")

    payment = await session.get(Payment, req.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status == "refunded":
        req.status = "failed"
        req.error_detail = "Payment was already refunded outside this request"
        req.resolved_at = datetime.utcnow()
        req.resolved_by = "admin"
        session.add(req)
        await session.commit()
        return {"status": "failed", "error": req.error_detail}

    if payment.provider == "yukassa":
        success, error = await yukassa_issue_refund(payment)
    elif payment.provider == "stars":
        success, error = await stars_issue_refund(payment, session)
    else:
        success, error = False, f"Unknown provider: {payment.provider}"

    req.status = "completed" if success else "failed"
    req.error_detail = None if success else error
    req.resolved_at = datetime.utcnow()
    req.resolved_by = "admin"
    session.add(req)
    await session.commit()

    user = await session.get(User, req.user_id)
    if user and user.email:
        await send_refund_decision_email(user.email, approved=success)

    if success:
        logger.info("Refund request %s completed (payment %s, provider %s)", req.id, payment.id, payment.provider)
        return {"status": "completed"}
    logger.error("Refund request %s failed (payment %s, provider %s): %s", req.id, payment.id, payment.provider, error)
    return {"status": "failed", "error": error}


class RejectRefundRequest(BaseModel):
    comment: str


@router.post("/admin/refunds/{request_id}/reject", dependencies=[Depends(is_admin)])
async def reject_refund(
    request_id: UUID,
    body: RejectRefundRequest,
    session: AsyncSession = Depends(get_session),
):
    if not body.comment or not body.comment.strip():
        raise HTTPException(status_code=422, detail="Comment is required")

    req = await session.get(RefundRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Refund request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already resolved (status={req.status})")

    req.status = "rejected"
    req.admin_comment = body.comment.strip()
    req.resolved_at = datetime.utcnow()
    req.resolved_by = "admin"
    session.add(req)
    await session.commit()

    user = await session.get(User, req.user_id)
    if user and user.email:
        await send_refund_decision_email(user.email, approved=False, admin_comment=req.admin_comment)

    logger.info("Refund request %s rejected: %s", req.id, req.admin_comment)
    return {"status": "rejected"}
