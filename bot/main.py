import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "")

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


async def main() -> None:
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        return
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
