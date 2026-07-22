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
from app.models.user import AuthProvider, Payment, RefundRequest, User

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)

PRODUCTS = {
    "pro_month": {"title": "Mystral Pro — Месяц", "stars": 199,  "rub": "399.00", "days": 30},
    "pro_year":  {"title": "Mystral Pro — Год",   "stars": 1599, "rub": "2999.00", "days": 365},
}

PAID_MARKER_TTL = 3600  # payload marker set by the bot after successful_payment

# A user who retries checkout (e.g. PaymentReturn's "Try again") while an
# earlier YuKassa payment for the same product is still pending would
# otherwise get a second checkout — and be charged twice for one Pro period
# if both later succeed. Reuse the still-open checkout within this window
# instead of creating a duplicate.
YUKASSA_PENDING_REUSE_WINDOW = timedelta(minutes=30)


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
    telegram_payment_charge_id: str = ""


class StarsRefundRequest(BaseModel):
    telegram_payment_charge_id: str


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


async def _record_stars_payment(user: User, product_key: str, charge_id: str, session: AsyncSession) -> None:
    """Persists a Payment row for a Stars purchase (provider="stars") so a later
    refund event has something to look up — mirrors the row YuKassa's /create
    endpoint writes for its own flow. Idempotent against activate retries: a
    charge_id already recorded is left alone rather than inserted again (the
    column is unique, so a naive re-insert would 500 on retry)."""
    if not charge_id:
        logger.warning("Stars activate: no telegram_payment_charge_id for user %s — refund lookup won't work", user.id)
        return
    result = await session.exec(select(Payment).where(Payment.provider_payment_id == charge_id))
    if result.first():
        return
    product = PRODUCTS.get(product_key, PRODUCTS["pro_month"])
    session.add(Payment(
        user_id=user.id,
        provider="stars",
        provider_payment_id=charge_id,
        product=product_key,
        amount=str(product["stars"]),
        currency="XTR",
        status="succeeded",
    ))
    await session.commit()


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

    await _record_stars_payment(user, product_key, req.telegram_payment_charge_id, session)

    r = aioredis.from_url(settings.redis_url)
    try:
        await r.setex(f"stars_paid:{req.payload}", PAID_MARKER_TTL, "1")
    finally:
        await r.close()

    logger.info("Stars activate: user %s activated %s via bot", user.id, product_key)
    return {"status": "ok"}


@router.post("/stars/refund", dependencies=[Depends(_require_internal_token)])
async def stars_refund(
    req: StarsRefundRequest,
    session: AsyncSession = Depends(get_session),
):
    """Called by the bot when Telegram delivers a refunded_payment update (Stars
    refund, whether user-initiated via Telegram or bot-initiated via
    refundStarPayment). Unlike YuKassa's public webhook, this arrives over the
    bot's own long-polling channel (already authenticated by the bot token), so
    there's no third-party body to distrust — the charge id is taken as given.
    Revokes on any refund, matching TZ-061's YuKassa policy (refundStarPayment
    has no amount parameter, so Stars refunds are full anyway, but we don't
    rely on that). Idempotent: a payment already "refunded" is left alone."""
    result = await session.exec(
        select(Payment).where(Payment.provider_payment_id == req.telegram_payment_charge_id)
    )
    payment = result.first()
    if not payment:
        logger.warning("Stars refund: no local row for charge %s", req.telegram_payment_charge_id)
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status == "refunded":
        return {"status": "ok"}

    payment.status = "refunded"
    payment.updated_at = datetime.utcnow()
    session.add(payment)
    await session.commit()

    user = await session.get(User, payment.user_id)
    if user:
        _revoke_pro(user)
        session.add(user)
        await session.commit()
        logger.info("Stars: user %s Pro revoked (charge %s)", payment.user_id, req.telegram_payment_charge_id)

    return {"status": "ok"}


class RefundRequestBody(BaseModel):
    reason: Optional[str] = None


REFUND_WINDOW_HOURS = 24


async def _find_refundable_payment(user_id: UUID, session: AsyncSession) -> Optional[Payment]:
    """Latest succeeded payment for the user that isn't already refunded and has
    no open (pending) or already-completed refund request against it. A payment
    whose prior request was rejected is left refundable — the user can ask again."""
    result = await session.exec(
        select(Payment)
        .where(Payment.user_id == user_id, Payment.status == "succeeded")
        .order_by(Payment.created_at.desc())
    )
    for payment in result.all():
        blocking = await session.exec(
            select(RefundRequest).where(
                RefundRequest.payment_id == payment.id,
                RefundRequest.status.in_(("pending", "completed")),
            )
        )
        if not blocking.first():
            return payment
    return None


@router.post("/refund-request")
async def refund_request(
    req: RefundRequestBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """TZ-065: creates a moderated RefundRequest instead of just emailing —
    the actual provider refund only happens once an admin approves it (see
    admin.py's /admin/refunds/{id}/approve)."""
    if current_user.subscription_tier != "pro":
        raise HTTPException(status_code=400, detail="No active Pro subscription")

    payment = await _find_refundable_payment(current_user.id, session)
    if not payment:
        raise HTTPException(status_code=400, detail="No eligible payment found")

    cutoff = datetime.utcnow() - timedelta(hours=REFUND_WINDOW_HOURS)
    if payment.created_at < cutoff:
        return {"status": "expired", "message": f"Refund period has expired ({REFUND_WINDOW_HOURS} hours)"}

    refund_req = RefundRequest(user_id=current_user.id, payment_id=payment.id, reason=req.reason or None)
    session.add(refund_req)
    await session.commit()
    await session.refresh(refund_req)

    await send_refund_email(
        to_admin="sasha.nechunaev1234@gmail.com",
        user_email=current_user.email or "",
        user_name=current_user.display_name or "",
        user_id=str(current_user.id),
        reason=req.reason or "",
        subscription_date=payment.created_at.isoformat(),
        provider=payment.provider,
        amount=f"{payment.amount} {payment.currency}",
    )

    logger.info("Refund request %s created: user %s, payment %s (%s)",
                refund_req.id, current_user.id, payment.id, payment.provider)
    return {"status": "sent", "request_id": str(refund_req.id)}


@router.get("/refund-request/status")
async def refund_request_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Latest refund request for the current user, if any — lets the profile
    page show pending/rejected(+comment)/completed/failed without polling admin data."""
    result = await session.exec(
        select(RefundRequest)
        .where(RefundRequest.user_id == current_user.id)
        .order_by(RefundRequest.created_at.desc())
    )
    latest = result.first()
    if not latest:
        return {"status": None}
    return {
        "status": latest.status,
        "admin_comment": latest.admin_comment,
        "created_at": latest.created_at.isoformat(),
        "resolved_at": latest.resolved_at.isoformat() if latest.resolved_at else None,
    }


async def yukassa_issue_refund(payment: Payment) -> tuple[bool, Optional[str]]:
    """Calls YuKassa's refund-creation API for a full refund of this payment.
    Returns (success, error_detail) — never raises, so a provider-side
    rejection (e.g. already refunded) surfaces as a clean failure, not a 500."""
    creds = base64.b64encode(
        f"{settings.yukassa_shop_id}:{settings.yukassa_secret_key}".encode()
    ).decode()
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(
                "https://api.yookassa.ru/v3/refunds",
                headers={
                    "Authorization": f"Basic {creds}",
                    "Idempotence-Key": str(uuid4()),
                },
                json={
                    "amount": {"value": payment.amount, "currency": payment.currency},
                    "payment_id": payment.provider_payment_id,
                },
            )
    except httpx.HTTPError:
        return False, "YuKassa request failed (network)"

    data = resp.json()
    if resp.status_code not in (200, 201):
        return False, data.get("description") or f"YuKassa error (status {resp.status_code})"
    return True, None


async def stars_issue_refund(payment: Payment, session: AsyncSession) -> tuple[bool, Optional[str]]:
    """Calls Telegram's refundStarPayment for this Stars payment. Needs the
    user's numeric Telegram id (Payment only stores our internal UUID),
    resolved via the linked AuthProvider row."""
    if not settings.telegram_bot_token:
        return False, "Telegram bot not configured"

    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.user_id == payment.user_id,
            AuthProvider.provider == "telegram",
        )
    )
    provider = result.first()
    if not provider:
        return False, "No linked Telegram account for this user"

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/refundStarPayment",
                json={
                    "user_id": int(provider.provider_id),
                    "telegram_payment_charge_id": payment.provider_payment_id,
                },
            )
    except httpx.HTTPError:
        return False, "Telegram request failed (network)"

    data = resp.json()
    if not data.get("ok"):
        return False, data.get("description") or "Telegram error"
    return True, None


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

    recent_cutoff = datetime.utcnow() - YUKASSA_PENDING_REUSE_WINDOW
    result = await session.exec(
        select(Payment)
        .where(
            Payment.user_id == current_user.id,
            Payment.provider == "yukassa",
            Payment.product == req.product,
            Payment.status == "pending",
            Payment.created_at >= recent_cutoff,
        )
        .order_by(Payment.created_at.desc())
    )
    existing = result.first()
    if existing:
        try:
            cached_meta = json.loads(existing.metadata_json or "{}")
            cached_url = cached_meta.get("confirmation_url") if isinstance(cached_meta, dict) else None
        except (ValueError, TypeError):
            cached_url = None
        if cached_url:
            return {"payment_url": cached_url, "payment_id": str(existing.id)}

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
    payment.metadata_json = json.dumps({"confirmation_url": payment_url})
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

    return {"status": payment.status, "tier": current_user.subscription_tier, "product": payment.product}
