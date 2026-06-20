import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import redis.asyncio as aioredis
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_session_context
from app.models.user import AuthProvider, UserProfile
from app.services.horoscope import (
    SIGNS_EMOJI,
    SIGNS_RU,
    generate_horoscope,
    zodiac_from_date,
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def _format_message(text: str, sign: str, lang: str) -> str:
    emoji = SIGNS_EMOJI.get(sign, "✨")
    if lang == "ru":
        return f"{emoji} <b>Гороскоп на сегодня</b>\n\n{text}\n\n<i>✨ Mystral</i>"
    return f"{emoji} <b>Today's horoscope</b>\n\n{text}\n\n<i>✨ Mystral</i>"


def _open_app_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Открыть Mystral ✨",
            url=f"https://t.me/Mystrallbot/app",
        )
    ]])


async def send_daily_horoscopes():
    if not settings.telegram_bot_token:
        return

    now_utc = datetime.now(ZoneInfo("UTC"))
    bot = Bot(token=settings.telegram_bot_token)
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
                sign_name = SIGNS_RU.get(sign, sign)
                text = await generate_horoscope(sign, lang)

                await bot.send_message(
                    chat_id=int(provider.provider_id),
                    text=_format_message(text, sign, lang),
                    parse_mode="HTML",
                    reply_markup=_open_app_keyboard(),
                )

                await redis.setex(redis_key, 90000, "1")
                logger.info("Sent daily horoscope to user %s (%s)", provider.user_id, sign_name)

            except Exception as e:
                logger.error("Failed to send notification to user %s: %s", provider.user_id, e)

    finally:
        await redis.close()
        await bot.session.close()
