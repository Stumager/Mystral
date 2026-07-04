from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.security import decode_jwt
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


async def _is_blacklisted(jti: str | None) -> bool:
    if not jti:
        return False
    try:
        from app.core.redis import redis_client
        if redis_client is None:
            return False
        return bool(await redis_client.exists(f"blacklist:{jti}"))
    except Exception:
        return False


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_jwt(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    if await _is_blacklisted(payload.get("jti")):
        raise HTTPException(status_code=401, detail="Token revoked")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account deactivated")

    if (
        user.subscription_tier == "pro"
        and user.subscription_expires_at
        and user.subscription_expires_at < datetime.utcnow()
    ):
        user.subscription_tier = "free"
        user.subscription_expires_at = None
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user
