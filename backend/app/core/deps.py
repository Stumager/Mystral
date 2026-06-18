from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.security import decode_jwt
from app.models.user import User

bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = decode_jwt(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
