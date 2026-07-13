import json
import random
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import bearer, get_current_user
from app.core.email import send_reset_email, send_verification_email
from app.core.security import (
    create_jwt,
    hash_password,
    validate_telegram_hash,
    validate_telegram_widget,
    verify_password,
)
from app.models.user import AuthProvider, User, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: Optional[str] = None
    widget_data: Optional[dict] = None


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LinkEmailRequest(BaseModel):
    email: str
    password: str


class TelegramLinkRequest(BaseModel):
    init_data: Optional[str] = None
    widget_data: Optional[dict] = None


class VerifyEmailRequest(BaseModel):
    email: str
    code: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResendVerificationRequest(BaseModel):
    email: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangeEmailRequest(BaseModel):
    new_email: str
    password: str


class ConfirmEmailChangeRequest(BaseModel):
    code: str


class DeleteAccountRequest(BaseModel):
    password: Optional[str] = None
    confirm: bool = False


def _validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "Пароль должен быть не менее 8 символов"
    if not re.search(r'[A-Z]', password):
        return "Пароль должен содержать заглавную букву"
    if not re.search(r'[0-9]', password):
        return "Пароль должен содержать цифру"
    return None


def _validate_name(name: str) -> str | None:
    """Final authoritative check backing the frontend's validateName (TZ-059).
    No SQL-character blocklist here — name is only ever bound via the ORM
    (parameterized), never concatenated into raw SQL, so that class of
    "protection" would just reject legitimate names for no real safety gain.
    str.isalpha() is the stdlib equivalent of a \\p{L} check (stdlib re has no
    Unicode property escapes) — works for any of the platform's 6 languages,
    not just a hardcoded alphabet list."""
    trimmed = name.strip()
    if not trimmed:
        return "Укажи имя"
    if len(trimmed) < 2:
        return "Минимум 2 символа"
    if len(trimmed) > 50:
        return "Максимум 50 символов"
    if "<" in name or ">" in name:
        return "Имя не должно содержать < или >"
    if not any(ch.isalpha() for ch in name):
        return "Имя должно содержать хотя бы одну букву"
    return None


def _get_ip(request: Request) -> str:
    # nginx appends the real client IP as the LAST entry of X-Forwarded-For;
    # taking the first entry would let clients spoof rate-limit keys.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


async def _check_ip_rate(ip: str, key_prefix: str, limit: int, window: int) -> None:
    r = aioredis.from_url(settings.redis_url)
    try:
        key = f"{key_prefix}:{ip}"
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window)
        if count > limit:
            raise HTTPException(429, "Слишком много попыток. Подождите.")
    finally:
        await r.close()


def _reactivate_if_needed(user: User, session: AsyncSession) -> None:
    """Logging in during the 30-day grace period cancels scheduled deletion."""
    if not user.is_active:
        user.is_active = True
        user.deletion_scheduled_at = None
        session.add(user)


class MergeRequest(BaseModel):
    init_data: Optional[str] = None
    widget_data: Optional[dict] = None
    email: str
    password: str


async def _user_response(user: User, token: str, session: AsyncSession) -> dict:
    profile_result = await session.exec(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.first()
    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "name": user.display_name,
            "lang": user.lang,
            "tier": user.subscription_tier,
            "has_birth_date": profile is not None and profile.birth_date is not None,
        },
    }


def _resolve_tg_id(req_init_data: Optional[str], req_widget_data: Optional[dict]) -> tuple[str, dict]:
    """Extract tg_id and user dict from either TMA init_data or Login Widget data."""
    if req_init_data:
        data = validate_telegram_hash(req_init_data)
        if not data:
            raise HTTPException(status_code=401, detail="Invalid Telegram auth")
        tg_user = json.loads(data.get("user", "{}"))
        tg_id = str(tg_user.get("id", ""))
    elif req_widget_data:
        data = validate_telegram_widget(req_widget_data)
        if not data:
            raise HTTPException(status_code=401, detail="Invalid Telegram widget auth")
        tg_user = data
        tg_id = str(data.get("id", ""))
    else:
        raise HTTPException(status_code=400, detail="No Telegram auth data provided")

    if not tg_id:
        raise HTTPException(status_code=400, detail="Could not extract Telegram user ID")

    return tg_id, tg_user


@router.post("/telegram")
async def auth_telegram(
    req: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    tg_id, tg_user = _resolve_tg_id(req.init_data, req.widget_data)

    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "telegram",
            AuthProvider.provider_id == tg_id,
        )
    )
    provider = result.first()
    is_new = provider is None

    if provider:
        user = await session.get(User, provider.user_id)
        if user:
            _reactivate_if_needed(user, session)
            await session.commit()
            await session.refresh(user)
    else:
        user = User(
            display_name=tg_user.get("first_name", ""),
            lang=tg_user.get("language_code", "ru"),
        )
        session.add(user)
        await session.flush()
        session.add(AuthProvider(
            user_id=user.id,
            provider="telegram",
            provider_id=tg_id,
        ))
        await session.commit()
        await session.refresh(user)

    response = await _user_response(user, create_jwt(str(user.id)), session)
    response["is_new"] = is_new
    return response


@router.post("/register")
async def register(
    req: RegisterRequest,
    request: Request,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    await _check_ip_rate(_get_ip(request), "register", 5, 3600)

    pwd_err = _validate_password(req.password)
    if pwd_err:
        raise HTTPException(400, pwd_err)

    name_err = _validate_name(req.name)
    if name_err:
        raise HTTPException(400, name_err)

    from email_validator import validate_email, EmailNotValidError
    try:
        validate_email(req.email, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Некорректный email")

    result = await session.exec(select(User).where(User.email == req.email))
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    code = str(random.randint(100000, 999999))
    user = User(
        email=req.email,
        display_name=req.name.strip(),
        email_verified=False,
        verification_code=code,
        verification_code_expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    session.add(user)
    await session.flush()

    session.add(AuthProvider(
        user_id=user.id,
        provider="email",
        provider_id=req.email,
        password_hash=hash_password(req.password),
    ))
    await session.commit()

    bg.add_task(send_verification_email, req.email, code)

    return {"status": "verification_required", "email": req.email}


@router.post("/login")
async def login(
    req: LoginRequest,
    request: Request,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    await _check_ip_rate(_get_ip(request), "login_attempts", 10, 900)

    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "email",
            AuthProvider.provider_id == req.email,
        )
    )
    provider = result.first()
    if not provider or not provider.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, provider.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = await session.get(User, provider.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    _reactivate_if_needed(user, session)

    if user.email and not user.email_verified:
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.verification_code_expires_at = datetime.utcnow() + timedelta(minutes=15)
        session.add(user)
        await session.commit()
        bg.add_task(send_verification_email, user.email, code)
        return {"status": "verification_required", "email": user.email}

    await session.commit()
    await session.refresh(user)
    return await _user_response(user, create_jwt(str(user.id)), session)


@router.post("/verify-email")
async def verify_email(
    req: VerifyEmailRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    await _check_ip_rate(_get_ip(request), "verify_email", 15, 3600)

    result = await session.exec(select(User).where(User.email == req.email))
    user = result.first()
    if not user:
        raise HTTPException(400, "Пользователь не найден")
    if user.email_verified:
        return await _user_response(user, create_jwt(str(user.id)), session)
    if not user.verification_code:
        raise HTTPException(400, "Код не запрошен")
    if user.verification_code_expires_at and user.verification_code_expires_at < datetime.utcnow():
        raise HTTPException(400, "Код истёк, запросите новый")

    # 6-digit codes are brute-forceable: cap wrong attempts per email
    r = aioredis.from_url(settings.redis_url)
    try:
        attempts_key = f"verify_attempts:{req.email}"
        if user.verification_code != req.code:
            attempts = await r.incr(attempts_key)
            if attempts == 1:
                await r.expire(attempts_key, 900)
            if attempts >= 5:
                user.verification_code = None
                user.verification_code_expires_at = None
                session.add(user)
                await session.commit()
                raise HTTPException(400, "Код истёк, запросите новый")
            raise HTTPException(400, "Неверный код")
        await r.delete(attempts_key)
    finally:
        await r.close()

    user.email_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return await _user_response(user, create_jwt(str(user.id)), session)


@router.post("/resend-verification")
async def resend_verification(
    req: ResendVerificationRequest,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(User).where(User.email == req.email))
    user = result.first()
    if not user:
        raise HTTPException(400, "Пользователь не найден")
    if user.email_verified:
        raise HTTPException(400, "Email уже подтверждён")

    r = aioredis.from_url(settings.redis_url)
    try:
        key = f"resend:{req.email}"
        if await r.exists(key):
            raise HTTPException(429, "Подождите минуту перед повторной отправкой")
        await r.setex(key, 60, "1")
    finally:
        await r.close()

    code = str(random.randint(100000, 999999))
    user.verification_code = code
    user.verification_code_expires_at = datetime.utcnow() + timedelta(minutes=15)
    session.add(user)
    await session.commit()

    bg.add_task(send_verification_email, req.email, code)

    return {"status": "sent"}


@router.post("/forgot-password")
async def forgot_password(
    req: ForgotPasswordRequest,
    request: Request,
    bg: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    await _check_ip_rate(_get_ip(request), "forgot_pwd", 3, 3600)
    result = await session.exec(select(User).where(User.email == req.email))
    user = result.first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        session.add(user)
        await session.commit()
        bg.add_task(send_reset_email, req.email, token)
    return {"status": "sent"}


@router.post("/reset-password")
async def reset_password(
    req: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(User).where(User.reset_token == req.token))
    user = result.first()
    if not user:
        raise HTTPException(400, "Недействительная ссылка")
    if user.reset_token_expires_at and user.reset_token_expires_at < datetime.utcnow():
        raise HTTPException(400, "Ссылка устарела. Запросите новую")
    if len(req.new_password) < 8:
        raise HTTPException(400, "Пароль должен быть не менее 8 символов")

    provider_result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == user.id, AuthProvider.provider == "email")
    )
    provider = provider_result.first()
    if provider:
        provider.password_hash = hash_password(req.new_password)
        session.add(provider)

    user.reset_token = None
    user.reset_token_expires_at = None
    session.add(user)
    await session.commit()
    return {"status": "ok"}


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == current_user.id, AuthProvider.provider == "email")
    )
    provider = result.first()
    if not provider or not provider.password_hash:
        raise HTTPException(400, "Аккаунт без пароля")
    if not verify_password(req.current_password, provider.password_hash):
        raise HTTPException(400, "Неверный текущий пароль")
    pwd_err = _validate_password(req.new_password)
    if pwd_err:
        raise HTTPException(400, pwd_err)
    provider.password_hash = hash_password(req.new_password)
    session.add(provider)
    await session.commit()
    return {"status": "ok"}


@router.post("/change-email")
async def change_email(
    req: ChangeEmailRequest,
    bg: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == current_user.id, AuthProvider.provider == "email")
    )
    provider = result.first()
    if not provider or not provider.password_hash:
        raise HTTPException(400, "Аккаунт без пароля")
    if not verify_password(req.password, provider.password_hash):
        raise HTTPException(400, "Неверный пароль")

    existing = await session.exec(select(User).where(User.email == req.new_email))
    if existing.first():
        raise HTTPException(400, "Email уже используется")

    code = str(random.randint(100000, 999999))
    current_user.pending_email = req.new_email
    current_user.pending_email_code = code
    current_user.pending_email_expires_at = datetime.utcnow() + timedelta(minutes=15)
    session.add(current_user)
    await session.commit()

    bg.add_task(send_verification_email, req.new_email, code)
    return {"status": "verification_required"}


@router.post("/confirm-email-change")
async def confirm_email_change(
    req: ConfirmEmailChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not current_user.pending_email or not current_user.pending_email_code:
        raise HTTPException(400, "Нет ожидающей смены email")
    if current_user.pending_email_expires_at and current_user.pending_email_expires_at < datetime.utcnow():
        raise HTTPException(400, "Код истёк")
    if current_user.pending_email_code != req.code:
        raise HTTPException(400, "Неверный код")

    old_email = current_user.email
    current_user.email = current_user.pending_email
    current_user.email_verified = True
    current_user.pending_email = None
    current_user.pending_email_code = None
    current_user.pending_email_expires_at = None
    session.add(current_user)

    provider_result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == current_user.id, AuthProvider.provider == "email")
    )
    provider = provider_result.first()
    if provider:
        provider.provider_id = current_user.email
        session.add(provider)

    await session.commit()
    return {"status": "ok"}


@router.delete("/account")
async def delete_account(
    req: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == current_user.id)
    )
    providers = result.all()

    has_email_provider = False
    for p in providers:
        if p.provider == "email" and p.password_hash:
            has_email_provider = True
            if not req.password:
                raise HTTPException(400, "Password required to delete account")
            if not verify_password(req.password, p.password_hash):
                raise HTTPException(400, "Invalid password")
            break

    if not has_email_provider:
        if not req.confirm:
            raise HTTPException(400, "Confirmation required to delete account")

    current_user.is_active = False
    current_user.deletion_scheduled_at = datetime.utcnow() + timedelta(days=30)
    session.add(current_user)
    await session.commit()

    return {
        "status": "scheduled",
        "deletion_date": current_user.deletion_scheduled_at.isoformat(),
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    credentials=Depends(bearer),
):
    """Blacklist the current token's jti until its natural expiry."""
    from app.core.security import decode_jwt

    try:
        payload = decode_jwt(credentials.credentials)
        jti = payload.get("jti")
        exp = payload.get("exp")
    except Exception:
        return {"status": "ok"}

    if jti:
        ttl = 30 * 86400
        if exp:
            ttl = max(int(exp - datetime.utcnow().timestamp()), 60)
        r = aioredis.from_url(settings.redis_url)
        try:
            await r.setex(f"blacklist:{jti}", ttl, "1")
        finally:
            await r.close()
    return {"status": "ok"}


@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == current_user.id)
    )
    providers = [p.provider for p in result.all()]
    profile_result = await session.exec(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.first()
    return {
        "id": str(current_user.id),
        "name": current_user.display_name,
        "lang": current_user.lang,
        "tier": current_user.subscription_tier,
        "providers": providers,
        "has_birth_date": profile is not None and profile.birth_date is not None,
    }


@router.post("/link-email")
async def link_email(
    req: LinkEmailRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    pwd_err = _validate_password(req.password)
    if pwd_err:
        raise HTTPException(400, pwd_err)

    from email_validator import validate_email, EmailNotValidError
    try:
        validate_email(req.email, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Некорректный email")

    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "email",
            AuthProvider.provider_id == req.email,
        )
    )
    if result.first():
        raise HTTPException(status_code=409, detail="Email already in use")

    session.add(AuthProvider(
        user_id=current_user.id,
        provider="email",
        provider_id=req.email,
        password_hash=hash_password(req.password),
    ))
    if not current_user.email:
        current_user.email = req.email
        session.add(current_user)
    await session.commit()
    return {"success": True}


@router.post("/link-telegram")
async def link_telegram(
    req: TelegramLinkRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    tg_id, _ = _resolve_tg_id(req.init_data, req.widget_data)

    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "telegram",
            AuthProvider.provider_id == tg_id,
        )
    )
    if result.first():
        raise HTTPException(status_code=409, detail="Telegram already linked to another account")

    session.add(AuthProvider(
        user_id=current_user.id,
        provider="telegram",
        provider_id=tg_id,
    ))
    await session.commit()
    return {"success": True}


@router.post("/merge")
async def merge_accounts(
    req: MergeRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    # Same limit as /login — this endpoint also verifies email+password
    await _check_ip_rate(_get_ip(request), "login_attempts", 10, 900)

    tg_id, _ = _resolve_tg_id(req.init_data, req.widget_data)

    # Validate email credentials
    email_result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "email",
            AuthProvider.provider_id == req.email,
        )
    )
    email_provider = email_result.first()
    if not email_provider or not verify_password(req.password, email_provider.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid email credentials")

    email_user = await session.get(User, email_provider.user_id)
    if not email_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Transfer or create TG provider on the email account
    tg_result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "telegram",
            AuthProvider.provider_id == tg_id,
        )
    )
    tg_provider = tg_result.first()

    if tg_provider:
        if tg_provider.user_id != email_user.id:
            tg_provider.user_id = email_user.id
            session.add(tg_provider)
    else:
        session.add(AuthProvider(
            user_id=email_user.id,
            provider="telegram",
            provider_id=tg_id,
        ))

    await session.commit()
    await session.refresh(email_user)
    return await _user_response(email_user, create_jwt(str(email_user.id)), session)
