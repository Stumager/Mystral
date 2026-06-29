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
from app.models.user import (
    AuthProvider,
    ReferralLog,
    Review,
    RuneReading,
    TarotReading,
    User,
    UserPartner,
    UserProfile,
)
from app.api.v1.lunar import get_lunar_today_data, get_upcoming_events
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
    lunar = get_lunar_today_data(lang)
    lunar_line = f"\n──────────────\n🌙 {lunar['lunar_day']}-й лунный день · {lunar['phase_name']}\n{lunar['day_title']}"
    if lunar["energy"] == "hecat":
        lunar_line += "\n⚠️ День Гекаты — будьте осторожны"
    if lang == "ru":
        return f"{emoji} <b>Гороскоп на сегодня</b>\n\n{text}{lunar_line}\n\n<i>✨ Mystral</i>"
    lunar_en = get_lunar_today_data("en")
    lunar_line_en = f"\n──────────────\n🌙 Lunar day {lunar_en['lunar_day']} · {lunar_en['phase_name']}\n{lunar_en['day_title']}"
    if lunar_en["energy"] == "hecat":
        lunar_line_en += "\n⚠️ Hecate Day — be careful"
    return f"{emoji} <b>Today's horoscope</b>\n\n{text}{lunar_line_en}\n\n<i>✨ Mystral</i>"


async def _send_tg_message(http: httpx.AsyncClient, chat_id: int, text: str) -> bool:
    webapp_url = settings.telegram_webapp_url
    keyboard = {
        "inline_keyboard": [[
            {"text": "Открыть Mystral", "web_app": {"url": webapp_url}} if webapp_url
            else {"text": "Открыть Mystral", "url": "https://t.me/Mystrallbot/app"}
        ]]
    }
    resp = await http.post(
        TG_API.format(token=settings.telegram_bot_token),
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": keyboard,
        },
    )
    if resp.status_code != 200:
        logger.error("TG sendMessage failed: %s %s", resp.status_code, resp.text[:200])
    return resp.status_code == 200


async def send_daily_horoscopes():
    if not settings.telegram_bot_token:
        logger.warning("Scheduler: no bot token, skipping")
        return

    now_utc = datetime.now(ZoneInfo("UTC"))
    logger.info("Scheduler tick at %s UTC", now_utc.strftime("%H:%M"))
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

        logger.info("Scheduler: found %d eligible users", len(results))

        async with httpx.AsyncClient(timeout=15) as http:
            for profile, provider in results:
                try:
                    tz = ZoneInfo(profile.timezone)
                    local_time = now_utc.astimezone(tz)
                    logger.debug("User %s: tz=%s, local=%s:%s",
                                 provider.user_id, profile.timezone, local_time.hour, local_time.minute)

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


async def cleanup_deleted_accounts():
    """Delete users whose deletion_scheduled_at has passed and is_active is False."""
    async with get_session_context() as session:
        stmt = select(User).where(
            User.is_active == False,  # noqa: E712
            User.deletion_scheduled_at.is_not(None),
            User.deletion_scheduled_at < datetime.utcnow(),
        )
        results = await session.exec(stmt)
        users = results.all()

        if not users:
            logger.info("Cleanup: no accounts to delete")
            return

        for user in users:
            uid = user.id

            for model in (TarotReading, RuneReading, Review, UserPartner, ReferralLog):
                rows = await session.exec(select(model).where(model.user_id == uid))
                for row in rows.all():
                    await session.delete(row)

            profile = await session.exec(
                select(UserProfile).where(UserProfile.user_id == uid)
            )
            for row in profile.all():
                await session.delete(row)

            providers = await session.exec(
                select(AuthProvider).where(AuthProvider.user_id == uid)
            )
            for row in providers.all():
                await session.delete(row)

            await session.delete(user)
            logger.info("Cleanup: deleted user %s", uid)

        await session.commit()
        logger.info("Cleanup: removed %d deleted accounts", len(users))


async def send_astro_event_notifications():
    if not settings.telegram_bot_token:
        return

    today_events = [e for e in get_upcoming_events(1, "ru") if e["days_until"] == 0]
    if not today_events:
        logger.info("Astro events: none today")
        return

    logger.info("Astro events today: %s", [e["type"] for e in today_events])
    redis = aioredis.from_url(settings.redis_url)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    try:
        async with get_session_context() as session:
            stmt = (
                select(UserProfile, AuthProvider)
                .join(AuthProvider, AuthProvider.user_id == UserProfile.user_id)
                .where(
                    UserProfile.notifications_enabled == True,  # noqa: E712
                    AuthProvider.provider == "telegram",
                )
            )
            results = (await session.exec(stmt)).all()

        async with httpx.AsyncClient(timeout=15) as http:
            for event in today_events:
                ev_ru = get_upcoming_events(1, "ru")
                ev_en = get_upcoming_events(1, "en")
                title_ru = next((e["title"] for e in ev_ru if e["type"] == event["type"]), event["title"])
                desc_ru = next((e["description"] for e in ev_ru if e["type"] == event["type"]), "")
                title_en = next((e["title"] for e in ev_en if e["type"] == event["type"]), event["title"])
                desc_en = next((e["description"] for e in ev_en if e["type"] == event["type"]), "")

                for profile, provider in results:
                    key = f"astro_notif:{event['type']}:{today_str}:{provider.user_id}"
                    if await redis.exists(key):
                        continue

                    msg = (
                        f"{event['icon']} <b>{title_ru}</b>\n\n"
                        f"{desc_ru}"
                    )
                    if await _send_tg_message(http, int(provider.provider_id), msg):
                        await redis.setex(key, 90000, "1")
                        logger.info("Sent astro event %s to user %s", event["type"], provider.user_id)

    except Exception as e:
        logger.error("Astro event notifications failed: %s", e)
    finally:
        await redis.close()
