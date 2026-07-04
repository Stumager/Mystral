import hashlib
import hmac
import urllib.parse
import uuid
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

JWT_TTL_DAYS = 30


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_jwt(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=JWT_TTL_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expire, "jti": uuid.uuid4().hex},
        settings.secret_key,
        algorithm="HS256",
    )


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def validate_telegram_hash(init_data: str) -> dict | None:
    parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash or not settings.telegram_bot_token:
        return None

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        settings.telegram_bot_token.encode(),
        hashlib.sha256,
    ).digest()

    computed = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        return None

    return parsed


def validate_telegram_widget_hash(data: dict) -> bool:
    """Boolean check for Telegram Login Widget data validity."""
    return validate_telegram_widget(data) is not None


def validate_telegram_widget(data: dict) -> dict | None:
    """Telegram Login Widget validation — uses SHA256(bot_token) as secret, not nested HMAC."""
    data = dict(data)
    received_hash = data.pop("hash", None)
    if not received_hash or not settings.telegram_bot_token:
        return None

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hashlib.sha256(settings.telegram_bot_token.encode()).digest()

    computed = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        return None

    return data
