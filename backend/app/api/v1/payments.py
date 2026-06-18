import base64
import json
from typing import Optional
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["payments"])

PRODUCTS = {
    "pro_month": {"title": "Mystral Pro — Месяц", "stars": 300,  "rub": "299.00"},
    "pro_year":  {"title": "Mystral Pro — Год",   "stars": 2400, "rub": "1990.00"},
}


class StarsCreateRequest(BaseModel):
    product: str


class StarsConfirmRequest(BaseModel):
    telegram_payment_charge_id: Optional[str] = ""
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
    current_user.subscription_tier = "pro"
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return {"status": "ok", "tier": "pro"}


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
    if not user_id:
        return {"status": "no_user_id"}

    from uuid import UUID
    from app.models.user import User as UserModel
    user = await session.get(UserModel, UUID(user_id))
    if user:
        user.subscription_tier = "pro"
        session.add(user)
        await session.commit()

    return {"status": "ok"}
