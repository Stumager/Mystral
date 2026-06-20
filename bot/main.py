import asyncio
import logging
import os

import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    button = InlineKeyboardButton(
        text="Открыть Mystral",
        web_app=WebAppInfo(url=WEBAPP_URL) if WEBAPP_URL else None,
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    await message.answer(
        "Добро пожаловать в Mystral!\n\nЭзотерическая платформа для вашего пути.",
        reply_markup=keyboard if WEBAPP_URL else None,
    )


@dp.message(Command("notifications"))
async def cmd_notifications(message: Message) -> None:
    if not message.from_user:
        return

    tg_id = str(message.from_user.id)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                f"{BACKEND_URL}/api/v1/profile/toggle-notifications",
                json={"telegram_id": tg_id},
            )
            if res.status_code == 404:
                await message.answer(
                    "Сначала авторизуйся в Mystral, чтобы управлять уведомлениями."
                )
                return

            data = res.json()
            enabled = data.get("notifications_enabled", False)

        if enabled:
            await message.answer(
                "🔔 Ежедневный гороскоп <b>включён</b>.\n"
                "Ты будешь получать гороскоп каждое утро в 9:00.\n\n"
                "Отключить: /notifications",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                "🔕 Ежедневный гороскоп <b>выключен</b>.\n\n"
                "Включить снова: /notifications",
                parse_mode="HTML",
            )
    except Exception as e:
        logger.error("Failed to toggle notifications: %s", e)
        await message.answer("Произошла ошибка. Попробуй позже.")


async def main() -> None:
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        return
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
