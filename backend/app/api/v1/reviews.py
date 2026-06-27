from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import Review, User, UserProfile

router = APIRouter()


class CreateReviewRequest(BaseModel):
    rating: int
    text: Optional[str] = None
    section: Optional[str] = None


@router.post("/reviews")
async def create_review(
    req: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(400, "Rating must be 1-5")
    if req.text and len(req.text) > 500:
        raise HTTPException(400, "Text max 500 characters")

    result = await session.exec(select(Review).where(Review.user_id == current_user.id))
    existing = result.first()

    if existing:
        existing.rating = req.rating
        existing.text = req.text
        existing.section = req.section
        existing.is_published = False
        session.add(existing)
        await session.commit()
        return {"status": "ok", "review_id": str(existing.id)}

    review = Review(user_id=current_user.id, rating=req.rating, text=req.text, section=req.section)
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return {"status": "ok", "review_id": str(review.id)}


@router.get("/reviews/my")
async def my_review(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Review).where(Review.user_id == current_user.id))
    review = result.first()
    if not review:
        return None
    return {"rating": review.rating, "text": review.text, "created_at": review.created_at.isoformat() if review.created_at else None}


@router.get("/reviews/public")
async def public_reviews(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    avg_result = await session.exec(
        select(func.avg(Review.rating)).where(Review.is_published == True)
    )
    avg = avg_result.one() or 0

    count_result = await session.exec(
        select(func.count()).select_from(Review).where(Review.is_published == True)
    )
    total = count_result.one()

    rows = (await session.exec(
        select(Review).where(Review.is_published == True)
        .order_by(Review.created_at.desc()).offset(offset).limit(limit)
    )).all()

    reviews = []
    for r in rows:
        user = await session.get(User, r.user_id)
        profile_q = await session.exec(select(UserProfile).where(UserProfile.user_id == r.user_id))
        profile = profile_q.first()
        zodiac = None
        if profile and profile.birth_date:
            from app.services.horoscope import zodiac_from_date
            zodiac = zodiac_from_date(profile.birth_date)

        reviews.append({
            "id": str(r.id),
            "user_name": user.display_name if user else "Anonymous",
            "zodiac_sign": zodiac,
            "rating": r.rating,
            "text": r.text,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {"reviews": reviews, "average_rating": round(float(avg), 1), "total_count": total}


@router.get("/reviews/stats")
async def review_stats(session: AsyncSession = Depends(get_session)):
    avg_result = await session.exec(
        select(func.avg(Review.rating)).where(Review.is_published == True)
    )
    avg = avg_result.one() or 0

    total_result = await session.exec(
        select(func.count()).select_from(Review).where(Review.is_published == True)
    )
    total = total_result.one()

    dist: dict[str, int] = {}
    for i in range(1, 6):
        cr = await session.exec(
            select(func.count()).select_from(Review).where(Review.is_published == True, Review.rating == i)
        )
        dist[str(i)] = cr.one()

    return {"average_rating": round(float(avg), 1), "total_published": total, "distribution": dist}
