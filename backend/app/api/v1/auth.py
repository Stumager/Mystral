import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.security import (
    create_jwt,
    hash_password,
    validate_telegram_hash,
    validate_telegram_widget,
    verify_password,
)
from app.models.user import AuthProvider, User

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


class MergeRequest(BaseModel):
    init_data: Optional[str] = None
    widget_data: Optional[dict] = None
    email: str
    password: str


def _user_response(user: User, token: str) -> dict:
    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "name": user.display_name,
            "lang": user.lang,
            "tier": user.subscription_tier,
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

    response = _user_response(user, create_jwt(str(user.id)))
    response["is_new"] = is_new
    return response


@router.post("/register")
async def register(
    req: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(User).where(User.email == req.email))
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=req.email, display_name=req.name)
    session.add(user)
    await session.flush()

    session.add(AuthProvider(
        user_id=user.id,
        provider="email",
        provider_id=req.email,
        password_hash=hash_password(req.password),
    ))
    await session.commit()
    await session.refresh(user)

    return _user_response(user, create_jwt(str(user.id)))


@router.post("/login")
async def login(
    req: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
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

    return _user_response(user, create_jwt(str(user.id)))


@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(AuthProvider).where(AuthProvider.user_id == current_user.id)
    )
    providers = [p.provider for p in result.all()]
    return {
        "id": str(current_user.id),
        "name": current_user.display_name,
        "lang": current_user.lang,
        "tier": current_user.subscription_tier,
        "providers": providers,
    }


@router.post("/link-email")
async def link_email(
    req: LinkEmailRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
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
    session: AsyncSession = Depends(get_session),
):
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
    return _user_response(email_user, create_jwt(str(email_user.id)))
