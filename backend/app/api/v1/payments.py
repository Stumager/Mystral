import base64
import hmac as hmac_mod
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.email import send_refund_email
from app.models.user import AuthProvider, User

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)

PRODUCTS = {
    "pro_month": {"title": "Mystral Pro — Месяц", "stars": 199,  "rub": "399.00", "days": 30},
    "pro_year":  {"title": "Mystral Pro — Год",   "stars": 1599, "rub": "2999.00", "days": 365},
}

PAID_MARKER_TTL = 3600  # payload marker set by the bot after successful_payment


def _parse_payload(payload: str) -> tuple[str, str]:
    """'pro_year_<id>' -> ('pro_year', '<id>'). Product validated against PRODUCTS."""
    parts = payload.rsplit("_", 1)
    if len(parts) != 2 or parts[0] not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Invalid payload")
    return parts[0], parts[1]


async def _find_user_by_payload_id(user_id_str: str, session: AsyncSession) -> Optional[User]:
    """Payload id is either our UUID (Mini App flow) or a numeric Telegram id (bot deep-link flow)."""
    try:
        return await session.get(User, UUID(user_id_str))
    except (ValueError, TypeError):
        pass
    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "telegram",
            AuthProvider.provider_id == user_id_str,
        )
    )
    provider = result.first()
    if provider:
        return await session.get(User, provider.user_id)
    return None


def _activate_pro(user: User, product_key: str) -> None:
    product = PRODUCTS.get(product_key, PRODUCTS["pro_month"])
    user.subscription_tier = "pro"
    user.subscription_expires_at = datetime.utcnow() + timedelta(days=product["days"])
    user.subscription_created_at = datetime.utcnow()


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
    """Frontend calls this after openInvoice reports 'paid'. The client event is
    spoofable, so activation only happens if the bot (successful_payment) already
    marked this payload as paid in Redis — or already activated the subscription."""
    product_key, payload_uid = _parse_payload(req.payload)
    if payload_uid != str(current_user.id):
        raise HTTPException(status_code=403, detail="Payload does not match user")

    if current_user.subscription_tier == "pro":
        return {"status": "ok", "tier": "pro"}

    r = aioredis.from_url(settings.redis_url)
    try:
        paid = await r.get(f"stars_paid:{req.payload}")
    finally:
        await r.close()

    if not paid:
        # Bot confirmation hasn't arrived yet — client should retry shortly
        return {"status": "pending", "tier": current_user.subscription_tier}

    _activate_pro(current_user, product_key)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    logger.info("Stars confirm: user %s activated %s (verified via bot marker)", current_user.id, product_key)
    return {"status": "ok", "tier": "pro"}


async def _require_internal_token(x_internal_token: str = Header("")):
    """Server-to-server auth for the bot. Uses ADMIN_TOKEN from env."""
    if not settings.admin_token or not hmac_mod.compare_digest(x_internal_token, settings.admin_token):
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/stars/activate", dependencies=[Depends(_require_internal_token)])
async def stars_activate(
    req: StarsActivateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Called by the bot after Telegram sends successful_payment — the authoritative signal."""
    product_key, user_id_str = _parse_payload(req.payload)

    user = await _find_user_by_payload_id(user_id_str, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    _activate_pro(user, product_key)
    session.add(user)
    await session.commit()

    r = aioredis.from_url(settings.redis_url)
    try:
        await r.setex(f"stars_paid:{req.payload}", PAID_MARKER_TTL, "1")
    finally:
        await r.close()

    logger.info("Stars activate: user %s activated %s via bot", user.id, product_key)
    return {"status": "ok"}


class RefundRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/refund-request")
async def refund_request(
    req: RefundRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.subscription_tier != "pro":
        raise HTTPException(status_code=400, detail="No active Pro subscription")

    if not current_user.subscription_created_at:
        raise HTTPException(status_code=400, detail="Subscription date unknown")

    cutoff = datetime.utcnow() - timedelta(hours=24)
    if current_user.subscription_created_at < cutoff:
        return {"status": "expired", "message": "Refund period has expired (24 hours)"}

    r = aioredis.from_url(settings.redis_url)
    try:
        dup_key = f"refund_req:{current_user.id}"
        if await r.exists(dup_key):
            raise HTTPException(status_code=400, detail="Refund request already submitted")
        await r.setex(dup_key, 86400, "1")
    finally:
        await r.close()

    await send_refund_email(
        to_admin="sasha.nechunaev1234@gmail.com",
        user_email=current_user.email or "",
        user_name=current_user.display_name or "",
        user_id=str(current_user.id),
        reason=req.reason or "",
        subscription_date=current_user.subscription_created_at.isoformat(),
    )

    return {"status": "sent"}


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
    """YuKassa webhooks are unsigned — re-fetch the payment from the YuKassa API
    and only trust status/metadata returned by YuKassa itself."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if body.get("event") != "payment.succeeded":
        return {"status": "ignored"}

    payment_id = body.get("object", {}).get("id")
    if not payment_id:
        return {"status": "no_payment_id"}

    if not settings.yukassa_shop_id or not settings.yukassa_secret_key:
        raise HTTPException(status_code=503, detail="YuKassa not configured")

    creds = base64.b64encode(
        f"{settings.yukassa_shop_id}:{settings.yukassa_secret_key}".encode()
    ).decode()
    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.get(
            f"https://api.yookassa.ru/v3/payments/{payment_id}",
            headers={"Authorization": f"Basic {creds}"},
        )
    if resp.status_code != 200:
        logger.warning("YuKassa webhook: verify failed for %s (%s)", payment_id, resp.status_code)
        raise HTTPException(status_code=400, detail="Payment verification failed")

    payment = resp.json()
    if payment.get("status") != "succeeded":
        return {"status": "not_succeeded"}

    metadata = payment.get("metadata", {})
    user_id = metadata.get("user_id")
    product_key = metadata.get("product", "pro_month")
    if not user_id:
        return {"status": "no_user_id"}

    try:
        user = await session.get(User, UUID(user_id))
    except (ValueError, TypeError):
        return {"status": "bad_user_id"}
    if user:
        _activate_pro(user, product_key)
        session.add(user)
        await session.commit()
        logger.info("YuKassa webhook: user %s activated %s (verified)", user_id, product_key)

    return {"status": "ok"}
