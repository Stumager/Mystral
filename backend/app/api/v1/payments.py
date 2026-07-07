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
from app.models.user import AuthProvider, Payment, User

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


def _revoke_pro(user: User) -> None:
    user.subscription_tier = "free"
    user.subscription_expires_at = None


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
    session: AsyncSession = Depends(get_session),
):
    product = PRODUCTS.get(req.product)
    if not product:
        raise HTTPException(status_code=422, detail="Unknown product")

    if not settings.yukassa_shop_id or not settings.yukassa_secret_key:
        raise HTTPException(status_code=503, detail="YuKassa not configured")

    creds = base64.b64encode(
        f"{settings.yukassa_shop_id}:{settings.yukassa_secret_key}".encode()
    ).decode()

    # YuKassa's own payment id only exists in the *response*, but return_url
    # must be in the request, so it can't reference YuKassa's id. Generate our
    # own row id first and put that in return_url instead — the frontend's
    # status/PaymentReturn flow looks payments up by this id, not YuKassa's.
    payment = Payment(
        user_id=current_user.id,
        provider_payment_id="",
        product=req.product,
        amount=product["rub"],
    )

    try:
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
                        "return_url": f"{settings.frontend_url}/?payment_id={payment.id}",
                    },
                    "capture": True,
                    "description": product["title"],
                    "metadata": {"user_id": str(current_user.id), "product": req.product},
                },
            )
    except httpx.HTTPError:
        logger.error("YuKassa create: request failed (network)")
        raise HTTPException(status_code=502, detail="YuKassa request failed")

    if resp.status_code not in (200, 201):
        logger.error("YuKassa create: unexpected status %s", resp.status_code)
        raise HTTPException(status_code=502, detail="YuKassa request failed")

    data = resp.json()
    yk_payment_id = data.get("id")
    payment_url = data.get("confirmation", {}).get("confirmation_url")
    if not payment_url or not yk_payment_id:
        raise HTTPException(status_code=502, detail="No confirmation URL from YuKassa")

    payment.provider_payment_id = yk_payment_id
    session.add(payment)
    await session.commit()

    return {"payment_url": payment_url, "payment_id": str(payment.id)}


async def _verify_and_sync_payment(payment_id: str, session: AsyncSession) -> Optional[Payment]:
    """Re-fetches the payment from YuKassa's API (authoritative source — never
    trust a webhook body alone) and syncs the local row's status. Activates Pro
    exactly once per payment: a payment already marked "succeeded" locally is
    left alone even if this runs again (webhook retries, or the status
    endpoint re-checking a pending payment), so repeated deliveries can't push
    subscription_expires_at forward for free."""
    creds = base64.b64encode(
        f"{settings.yukassa_shop_id}:{settings.yukassa_secret_key}".encode()
    ).decode()
    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.get(
            f"https://api.yookassa.ru/v3/payments/{payment_id}",
            headers={"Authorization": f"Basic {creds}"},
        )
    if resp.status_code != 200:
        logger.warning("YuKassa verify: failed for %s (%s)", payment_id, resp.status_code)
        return None

    yk_payment = resp.json()
    result = await session.exec(select(Payment).where(Payment.provider_payment_id == payment_id))
    payment = result.first()
    if not payment:
        logger.warning("YuKassa verify: no local row for %s", payment_id)
        return None

    yk_status = yk_payment.get("status")
    was_succeeded = payment.status == "succeeded"
    if yk_status in ("succeeded", "canceled"):
        payment.status = yk_status
    payment.updated_at = datetime.utcnow()
    session.add(payment)
    await session.commit()
    await session.refresh(payment)

    if payment.status == "succeeded" and not was_succeeded:
        metadata = yk_payment.get("metadata", {})
        user_id = metadata.get("user_id")
        product_key = metadata.get("product", "pro_month")
        if user_id:
            try:
                user = await session.get(User, UUID(user_id))
            except (ValueError, TypeError):
                user = None
            if user:
                _activate_pro(user, product_key)
                session.add(user)
                await session.commit()
                logger.info("YuKassa: user %s activated %s (payment %s)", user_id, product_key, payment_id)

    return payment


async def _verify_and_revoke_refund(refund_id: str, session: AsyncSession) -> Optional[Payment]:
    """Re-fetches the refund from YuKassa's API (never trust webhook body alone —
    same discipline as _verify_and_sync_payment), resolves the local Payment via
    the verified refund's payment_id, and revokes Pro from that payment's user.
    Any refund amount (full or partial) revokes access — no amount comparison,
    per product decision. Idempotent: a payment already marked "refunded" is
    left alone on repeat webhook delivery, so retries don't re-log/re-touch it."""
    creds = base64.b64encode(
        f"{settings.yukassa_shop_id}:{settings.yukassa_secret_key}".encode()
    ).decode()
    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.get(
            f"https://api.yookassa.ru/v3/refunds/{refund_id}",
            headers={"Authorization": f"Basic {creds}"},
        )
    if resp.status_code != 200:
        logger.warning("YuKassa refund verify: failed for %s (%s)", refund_id, resp.status_code)
        return None

    yk_refund = resp.json()
    if yk_refund.get("status") != "succeeded":
        logger.warning("YuKassa refund verify: refund %s not succeeded (status=%s)", refund_id, yk_refund.get("status"))
        return None

    payment_id = yk_refund.get("payment_id")
    if not payment_id:
        logger.warning("YuKassa refund verify: no payment_id on refund %s", refund_id)
        return None

    result = await session.exec(select(Payment).where(Payment.provider_payment_id == payment_id))
    payment = result.first()
    if not payment:
        logger.warning("YuKassa refund verify: no local row for payment %s (refund %s)", payment_id, refund_id)
        return None

    was_refunded = payment.status == "refunded"
    payment.status = "refunded"
    payment.updated_at = datetime.utcnow()
    session.add(payment)
    await session.commit()
    await session.refresh(payment)

    if not was_refunded:
        user = await session.get(User, payment.user_id)
        if user:
            _revoke_pro(user)
            session.add(user)
            await session.commit()
            logger.info("YuKassa: user %s Pro revoked (refund %s, payment %s)", payment.user_id, refund_id, payment_id)

    return payment


@router.post("/yukassa/webhook")
async def yukassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """YuKassa webhooks are unsigned — _verify_and_sync_payment/_verify_and_revoke_refund
    re-fetch the object from the YuKassa API and only trust status/metadata YuKassa
    itself returns, never the webhook body directly."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = body.get("event")
    if event not in ("payment.succeeded", "payment.canceled", "refund.succeeded"):
        return {"status": "ignored"}

    if not settings.yukassa_shop_id or not settings.yukassa_secret_key:
        raise HTTPException(status_code=503, detail="YuKassa not configured")

    # object.id means different things per event: for payment.* it IS the
    # payment id; for refund.* it's the refund's own id, and the originating
    # payment_id only appears inside the verified refund object (see below).
    object_id = body.get("object", {}).get("id")

    if event == "refund.succeeded":
        if not object_id:
            return {"status": "no_refund_id"}
        payment = await _verify_and_revoke_refund(object_id, session)
    else:
        if not object_id:
            return {"status": "no_payment_id"}
        payment = await _verify_and_sync_payment(object_id, session)

    if not payment:
        raise HTTPException(status_code=400, detail="Verification failed")

    return {"status": "ok"}


@router.get("/yukassa/status/{payment_id}")
async def yukassa_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """payment_id here is OUR row id (embedded in return_url at create time),
    not YuKassa's own payment id — see yukassa_create's comment."""
    try:
        payment = await session.get(Payment, UUID(payment_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail="Payment not found")
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if payment.status == "pending" and settings.yukassa_shop_id and settings.yukassa_secret_key:
        synced = await _verify_and_sync_payment(payment.provider_payment_id, session)
        if synced:
            payment = synced
            await session.refresh(current_user)

    return {"status": payment.status, "tier": current_user.subscription_tier}
