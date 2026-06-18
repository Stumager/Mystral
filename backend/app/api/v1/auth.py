import json

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
    verify_password,
)
from app.models.user import AuthProvider, User

router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _user_response(user: User, token: str) -> dict:
    return {
        "access_token": token,
        "user": {"id": str(user.id), "name": user.display_name, "lang": user.lang},
    }


@router.post("/telegram")
async def auth_telegram(
    req: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    data = validate_telegram_hash(req.init_data)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")

    tg_user = json.loads(data.get("user", "{}"))
    tg_id = str(tg_user.get("id", ""))
    if not tg_id:
        raise HTTPException(status_code=400, detail="No user data in initData")

    result = await session.exec(
        select(AuthProvider).where(
            AuthProvider.provider == "telegram",
            AuthProvider.provider_id == tg_id,
        )
    )
    provider = result.first()

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

    return _user_response(user, create_jwt(str(user.id)))


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
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.display_name,
        "lang": current_user.lang,
    }
