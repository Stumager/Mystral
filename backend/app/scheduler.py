import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import redis.asyncio as aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_session_context
from app.models.user import AuthProvider, User, UserProfile
from app.services.horoscope import (
    SIGNS_EMOJI,
    SIGNS_RU,
    generate_horoscope,
    zodiac_from_date,
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

TG_API = "https://api.telegram.org/bot{token}/sendMessage"


def _format_message(text: str, sign: str, lang: str) -> str:
    emoji = SIGNS_EMOJI.get(sign, "✨")
    if lang == "ru":
        return f"{emoji} <b>Гороскоп на сегодня</b>\n\n{text}\n\n<i>✨ Mystral</i>"
    return f"{emoji} <b>Today's horoscope</b>\n\n{text}\n\n<i>✨ Mystral</i>"


async def _send_tg_message(http: httpx.AsyncClient, chat_id: int, text: str) -> bool:
    keyboard = {
        "inline_keyboard": [[
            {"text": "Открыть Mystral ✨", "url": "https://t.me/Mystrallbot/app"}
        ]]
    }
    resp = await http.post(
        TG_API.format(token=settings.telegram_bot_token),
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard),
        },
    )
    return resp.status_code == 200


async def send_daily_horoscopes():
    if not settings.telegram_bot_token:
        return

    now_utc = datetime.now(ZoneInfo("UTC"))
    redis = aioredis.from_url(settings.redis_url)

    try:
        async with get_session_context() as session:
            stmt = (
                select(UserProfile, AuthProvider)
                .join(AuthProvider, AuthProvider.user_id == UserProfile.user_id)
                .where(
                    UserProfile.notifications_enabled == True,  # noqa: E712
                    UserProfile.timezone.is_not(None),
                    UserProfile.birth_date.is_not(None),
                    AuthProvider.provider == "telegram",
                )
            )
            results = (await session.exec(stmt)).all()

        async with httpx.AsyncClient(timeout=15) as http:
            for profile, provider in results:
                try:
                    tz = ZoneInfo(profile.timezone)
                    local_time = now_utc.astimezone(tz)

                    if local_time.hour != 9 or local_time.minute >= 5:
                        continue

                    today = local_time.strftime("%Y-%m-%d")
                    redis_key = f"daily_notif:{provider.user_id}:{today}"
                    if await redis.exists(redis_key):
                        continue

                    sign = zodiac_from_date(profile.birth_date)
                    lang = "ru"
                    text = await generate_horoscope(sign, lang)
                    msg = _format_message(text, sign, lang)

                    ok = await _send_tg_message(http, int(provider.provider_id), msg)
                    if ok:
                        await redis.setex(redis_key, 90000, "1")
                        logger.info("Sent daily horoscope to user %s (%s)",
                                    provider.user_id, SIGNS_RU.get(sign, sign))
                    else:
                        logger.warning("TG API failed for user %s", provider.user_id)

                except Exception as e:
                    logger.error("Failed notification for user %s: %s", provider.user_id, e)

    finally:
        await redis.close()


async def send_subscription_reminders():
    if not settings.telegram_bot_token:
        return

    today = datetime.utcnow().date()
    in_3_days = today + timedelta(days=3)
    redis = aioredis.from_url(settings.redis_url)

    try:
        async with get_session_context() as session:
            stmt = (
                select(User, AuthProvider)
                .join(AuthProvider, AuthProvider.user_id == User.id)
                .where(
                    User.subscription_tier == "pro",
                    User.subscription_expires_at.is_not(None),
                    AuthProvider.provider == "telegram",
                )
            )
            results = (await session.exec(stmt)).all()

        async with httpx.AsyncClient(timeout=15) as http:
            for user, provider in results:
                exp_date = user.subscription_expires_at.date()
                chat_id = int(provider.provider_id)
                today_str = today.isoformat()

                if exp_date == in_3_days:
                    key = f"reminder_3d:{user.id}:{today_str}"
                    if await redis.exists(key):
                        continue
                    msg = (
                        "⚠️ Твоя подписка <b>Mystral Pro</b> истекает через 3 дня.\n"
                        "Продли, чтобы не потерять доступ."
                    )
                    if await _send_tg_message(http, chat_id, msg):
                        await redis.setex(key, 90000, "1")
                        logger.info("Sent 3-day reminder to user %s", user.id)

                elif exp_date == today:
                    key = f"reminder_exp:{user.id}:{today_str}"
                    if await redis.exists(key):
                        continue
                    msg = (
                        "❌ Подписка <b>Mystral Pro</b> истекла.\n"
                        "Возобнови доступ ко всем функциям."
                    )
                    if await _send_tg_message(http, chat_id, msg):
                        await redis.setex(key, 90000, "1")
                        logger.info("Sent expiry reminder to user %s", user.id)

    except Exception as e:
        logger.error("Subscription reminders failed: %s", e)
    finally:
        await redis.close()
