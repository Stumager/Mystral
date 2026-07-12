import asyncio
import logging
import os

import httpx
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    WebAppInfo,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
SUPPORT_TG_ID = os.getenv("SUPPORT_TELEGRAM_ID", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class SupportStates(StatesGroup):
    waiting_for_message = State()


PLANS = {
    "pay_month": {"title": "Mystral Pro — Месяц", "amount": 199, "payload_key": "pro_month"},
    "pay_year":  {"title": "Mystral Pro — Год",   "amount": 1599, "payload_key": "pro_year"},
}


async def send_stars_invoice(message: Message, plan_key: str) -> None:
    plan = PLANS.get(plan_key)
    if not plan or not message.from_user:
        return
    payload = f"{plan['payload_key']}_{message.from_user.id}"
    await message.answer_invoice(
        title=plan["title"],
        description="Безлимитные предсказания Mystral",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label="Mystral Pro", amount=plan["amount"])],
    )


@dp.message(CommandStart(deep_link=True))
async def cmd_start_deep(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    args = message.text or ""
    deep = args.split(maxsplit=1)[1] if len(args.split()) > 1 else ""

    if deep in PLANS:
        await send_stars_invoice(message, deep)
        return

    if "support" in deep:
        await state.set_state(SupportStates.waiting_for_message)
        await message.answer(
            "Опиши свою проблему — я передам её команде Mystral.\n"
            "Обычно отвечаем в течение нескольких часов."
        )
        return

    button = InlineKeyboardButton(
        text="Открыть Mystral",
        web_app=WebAppInfo(url=WEBAPP_URL) if WEBAPP_URL else None,
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(
        "Добро пожаловать в Mystral!\n\nЭзотерическая платформа для вашего пути.",
        reply_markup=keyboard if WEBAPP_URL else None,
    )


@dp.message(CommandStart())
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


@dp.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext) -> None:
    await state.set_state(SupportStates.waiting_for_message)
    await message.answer(
        "📩 Опиши свою проблему — я передам её команде Mystral.\n"
        "Обычно отвечаем в течение нескольких часов."
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
                headers={"X-Internal-Token": ADMIN_TOKEN},
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


@dp.message(SupportStates.waiting_for_message)
async def handle_support_message(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return

    await state.clear()

    if not SUPPORT_TG_ID:
        await message.answer("Поддержка временно недоступна.")
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "нет"

    support_text = (
        f"🆘 <b>Обращение в поддержку</b>\n\n"
        f"👤 Имя: {user.full_name}\n"
        f"🔗 Username: {username} / tg_id: {user.id}\n\n"
        f"💬 {message.text}"
    )

    try:
        sent = await bot.send_message(
            chat_id=int(SUPPORT_TG_ID),
            text=support_text,
            parse_mode="HTML",
        )

        r = aioredis.from_url(REDIS_URL)
        await r.setex(f"support:{sent.message_id}", 604800, str(user.id))
        await r.close()

        await message.answer(
            "✅ Сообщение отправлено в поддержку. Мы ответим в ближайшее время!"
        )
        logger.info("Support message from %s (tg_id=%s)", user.full_name, user.id)
    except Exception as e:
        logger.error("Failed to forward support message: %s", e)
        await message.answer("Не удалось отправить сообщение. Попробуй позже.")


@dp.message(F.reply_to_message)
async def handle_admin_reply(message: Message) -> None:
    if not message.from_user or not message.text or not SUPPORT_TG_ID:
        return
    if str(message.from_user.id) != SUPPORT_TG_ID:
        return
    if not message.reply_to_message:
        return

    replied_id = message.reply_to_message.message_id

    try:
        r = aioredis.from_url(REDIS_URL)
        user_tg_id = await r.get(f"support:{replied_id}")
        await r.close()

        if not user_tg_id:
            await message.answer("Не удалось определить пользователя (ключ истёк).")
            return

        await bot.send_message(
            chat_id=int(user_tg_id),
            text=f"💬 <b>Ответ поддержки Mystral:</b>\n\n{message.text}",
            parse_mode="HTML",
        )
        await message.answer("✅ Ответ доставлен.")
        logger.info("Support reply sent to tg_id=%s", user_tg_id.decode())
    except Exception as e:
        logger.error("Failed to deliver support reply: %s", e)
        await message.answer("Ошибка доставки ответа.")


@dp.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)
    logger.info("Pre-checkout approved: payload=%s", query.invoice_payload)


@dp.message(F.successful_payment)
async def on_successful_payment(message: Message) -> None:
    payment = message.successful_payment
    if not payment:
        return

    payload = payment.invoice_payload
    logger.info("Successful payment: payload=%s, amount=%s %s",
                payload, payment.total_amount, payment.currency)

    activated = False
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.post(
                    f"{BACKEND_URL}/api/v1/payments/stars/activate",
                    json={
                        "payload": payload,
                        "telegram_payment_charge_id": payment.telegram_payment_charge_id,
                    },
                    headers={"X-Internal-Token": ADMIN_TOKEN},
                )
                if res.status_code == 200:
                    logger.info("Pro activated via bot for payload=%s", payload)
                    activated = True
                    break
                logger.error("Activate failed (try %d): %s %s", attempt + 1, res.status_code, res.text)
        except Exception as e:
            logger.error("Failed to activate after payment (try %d): %s", attempt + 1, e)
        await asyncio.sleep(2)

    if not activated and SUPPORT_TG_ID:
        try:
            await bot.send_message(
                chat_id=int(SUPPORT_TG_ID),
                text=f"⚠️ ОПЛАТА НЕ АКТИВИРОВАНА: payload={payload}. Активируй вручную.",
            )
        except Exception:
            pass

    if message.from_user:
        await message.answer(
            "✨ <b>Mystral Pro активирован!</b>\n\n"
            "Все функции разблокированы. Приятного пользования!",
            parse_mode="HTML",
        )


@dp.message(F.refunded_payment)
async def on_refunded_payment(message: Message) -> None:
    """Telegram delivers this as a normal message update (same mechanism as
    successful_payment) when a Stars payment is refunded — whether the user
    requested it via Telegram themselves, or we call refundStarPayment. No
    separate update-type subscription is needed since the bot already polls
    for "message" updates."""
    refund = message.refunded_payment
    if not refund:
        return

    charge_id = refund.telegram_payment_charge_id
    tg_id = message.from_user.id if message.from_user else None
    logger.info("Refunded payment: charge_id=%s, tg_id=%s, amount=%s %s",
                charge_id, tg_id, refund.total_amount, refund.currency)

    revoked = False
    not_found = False
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.post(
                    f"{BACKEND_URL}/api/v1/payments/stars/refund",
                    json={"telegram_payment_charge_id": charge_id},
                    headers={"X-Internal-Token": ADMIN_TOKEN},
                )
                if res.status_code == 200:
                    revoked = True
                    break
                if res.status_code == 404:
                    not_found = True
                    break
                logger.error("Refund revoke failed (try %d): %s %s", attempt + 1, res.status_code, res.text)
        except Exception as e:
            logger.error("Failed to process refund (try %d): %s", attempt + 1, e)
        await asyncio.sleep(2)

    if not revoked and SUPPORT_TG_ID:
        reason = "платёж не найден в БД" if not_found else "ошибка сервера"
        try:
            await bot.send_message(
                chat_id=int(SUPPORT_TG_ID),
                text=(f"⚠️ ВОЗВРАТ STARS НЕ ОБРАБОТАН ({reason}): "
                      f"charge_id={charge_id}, tg_id={tg_id}. Отзови Pro вручную."),
            )
        except Exception:
            pass


async def main() -> None:
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        return
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
