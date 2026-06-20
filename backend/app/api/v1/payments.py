import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import AuthProvider, User

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)

PRODUCTS = {
    "pro_month": {"title": "Mystral Pro — Месяц", "stars": 150,  "rub": "149.00", "days": 30},
    "pro_year":  {"title": "Mystral Pro — Год",   "stars": 1200, "rub": "990.00", "days": 365},
}


def _activate_pro(user: User, product_key: str) -> None:
    product = PRODUCTS.get(product_key, PRODUCTS["pro_month"])
    user.subscription_tier = "pro"
    user.subscription_expires_at = datetime.utcnow() + timedelta(days=product["days"])


class StarsCreateRequest(BaseModel):
    product: str


class StarsConfirmRequest(BaseModel):
    telegram_payment_charge_id: Optional[str] = ""
    payload: str


class StarsActivateRequest(BaseModel):
    payload: str


class YukassaCreateRequest(BaseModel):
    product: str


@router.post("/stars/create")
async def stars_create(
    req: StarsCreateRequest,
    current_user: User = Depends(get_current_user),
):
    product = PRODUCTS.get(req.product)
    if not product:
        raise HTTPException(status_code=422, detail="Unknown product")

    if not settings.telegram_bot_token:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")

    payload = f"{req.product}_{current_user.id}"

    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/createInvoiceLink",
            json={
                "title": product["title"],
                "description": "Безлимитные предсказания Mystral",
                "payload": payload,
                "provider_token": "",
                "currency": "XTR",
                "prices": [{"label": "Mystral Pro", "amount": product["stars"]}],
            },
        )

    data = resp.json()
    if not data.get("ok"):
        raise HTTPException(status_code=500, detail=f"Telegram error: {data.get('description')}")

    return {"invoice_link": data["result"], "payload": payload}


@router.post("/stars/confirm")
async def stars_confirm(
    req: StarsConfirmRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    product_key = req.payload.split("_")[0] if "_" in req.payload else "pro_month"
    _activate_pro(current_user, product_key)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    logger.info("Stars confirm: user %s activated %s via frontend", current_user.id, product_key)
    return {"status": "ok", "tier": "pro"}


@router.post("/stars/activate")
async def stars_activate(
    req: StarsActivateRequest,
    session: AsyncSession = Depends(get_session),
):
    parts = req.payload.rsplit("_", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid payload")

    product_key, user_id_str = parts[0], parts[1]

    try:
        user = await session.get(User, UUID(user_id_str))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    _activate_pro(user, product_key)
    session.add(user)
    await session.commit()
    logger.info("Stars activate: user %s activated %s via bot", user.id, product_key)
    return {"status": "ok"}


@router.post("/yukassa/create")
async def yukassa_create(
    req: YukassaCreateRequest,
    current_user: User = Depends(get_current_user),
):
    product = PRODUCTS.get(req.product)
    if not product:
        raise HTTPException(status_code=422, detail="Unknown product")

    if not settings.yukassa_shop_id or not settings.yukassa_secret_key:
        raise HTTPException(status_code=503, detail="YuKassa not configured")

    creds = base64.b64encode(
        f"{settings.yukassa_shop_id}:{settings.yukassa_secret_key}".encode()
    ).decode()

    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.post(
            "https://api.yookassa.ru/v3/payments",
            headers={
                "Authorization": f"Basic {creds}",
                "Idempotence-Key": str(uuid4()),
            },
            json={
                "amount": {"value": product["rub"], "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.telegram_webapp_url or "https://t.me",
                },
                "capture": True,
                "description": product["title"],
                "metadata": {"user_id": str(current_user.id), "product": req.product},
            },
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail="YuKassa request failed")

    data = resp.json()
    payment_url = data.get("confirmation", {}).get("confirmation_url")
    if not payment_url:
        raise HTTPException(status_code=502, detail="No confirmation URL from YuKassa")

    return {"payment_url": payment_url, "payment_id": data.get("id")}


@router.post("/yukassa/webhook")
async def yukassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if body.get("event") != "payment.succeeded":
        return {"status": "ignored"}

    metadata = body.get("object", {}).get("metadata", {})
    user_id = metadata.get("user_id")
    product_key = metadata.get("product", "pro_month")
    if not user_id:
        return {"status": "no_user_id"}

    user = await session.get(User, UUID(user_id))
    if user:
        _activate_pro(user, product_key)
        session.add(user)
        await session.commit()
        logger.info("YuKassa webhook: user %s activated %s", user_id, product_key)

    return {"status": "ok"}
