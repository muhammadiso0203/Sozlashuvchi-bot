from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

private_router = Router(name="private_router")
private_router.message.filter(F.chat.type == "private")

def get_start_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    """Start xabari ostidagi inline tugmalar."""
    add_group_url = f"https://t.me/{bot_username}?startgroup=true"

    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Guruhga qo'shish",
                url=add_group_url
            )
        ],
        [
            InlineKeyboardButton(
                text="📖 Qo'llanma",
                callback_data="help_info"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@private_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    """Shaxsiy chatda /start buyrug'i."""
    db.add_user(message.from_user.id)
    bot_info = await bot.get_me()

    text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>! 👋\n\n"
        "🤖 <b>Men Telegram guruhlarida suhbatlashuvchi aqlli botman!</b>\n\n"
        "<b>Meni ishlatish uchun:</b>\n"
        "1. Quyidagi <b>«➕ Guruhga qo'shish»</b> tugmasi orqali meni guruhingizga qo'shing.\n"
        "2. Guruh a'zolari yozgan so'zlar va savollarga avtomatik javob qaytaraman.\n"
        "3. Guruhda menga reply qilinsa yoki <code>@{bot_username}</code> deb chaqirilsa, darhol javob beraman 😊\n\n"
        "➕ <i>Quyidagi tugmani bosing va guruhingizni tanlang:</i>"
    ).format(bot_username=bot_info.username)

    await message.reply(
        text,
        reply_markup=get_start_keyboard(bot_info.username),
        parse_mode="HTML"
    )

@private_router.callback_query(F.data == "help_info")
async def cb_help_info(callback: CallbackQuery, bot: Bot):
    """Qo'llanma tugmasi bosilganda."""
    text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "🔹 <b>Guruh sozlamasi:</b>\n"
        "Bot guruhdagi barcha xabarlarni o'qiy olishi uchun <b>@BotFather</b> ga kiring:\n"
        "1. <code>/mybots</code> -> botingizni tanlang.\n"
        "2. <b>Bot Settings</b> -> <b>Group Privacy</b> -> <b>Turn off</b> qiling.\n\n"
        "🔹 <b>Admin buyruqlari:</b>\n"
        "• <code>/admin</code> - Tugmali admin panelini ochish.\n"
        "• <code>/stats</code> - Obunachilar va guruhlar statistikasi.\n"
        "• <code>/groups</code> - Bot qo'shilgan guruhlar va adminlik holati.\n"
        "• <code>/add exact | kalit_so'z | javob</code> - Aniq mos kelganda javob berish.\n"
        "• <code>/add contains | ibora | javob</code> - Matn ichida uchrashganda javob berish.\n"
        "• <code>/del kalit_so'z</code> - Kalit so'zni o'chirish."
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_start")]
    ])
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")
    await callback.answer()

@private_router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery, bot: Bot):
    """Orqaga qaytish."""
    bot_info = await bot.get_me()
    text = (
        f"Assalomu alaykum, <b>{callback.from_user.full_name}</b>! 👋\n\n"
        "🤖 <b>Men Telegram guruhlarida suhbatlashuvchi aqlli botman!</b>\n\n"
        "<b>Meni ishlatish uchun:</b>\n"
        "1. Quyidagi <b>«➕ Guruhga qo'shish»</b> tugmasi orqali meni guruhingizga qo'shing.\n"
        "2. Guruh a'zolari yozgan so'zlar va savollarga avtomatik javob qaytaraman.\n"
        "3. Guruhda menga reply qilinsa yoki <code>@{bot_username}</code> deb chaqirilsa, darhol javob beraman 😊\n\n"
        "➕ <i>Quyidagi tugmani bosing va guruhingizni tanlang:</i>"
    ).format(bot_username=bot_info.username)

    await callback.message.edit_text(
        text,
        reply_markup=get_start_keyboard(bot_info.username),
        parse_mode="HTML"
    )
    await callback.answer()

@private_router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam komandasi."""
    db.add_user(message.from_user.id)
    text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "🔹 <b>Guruh sozlamasi:</b>\n"
        "Bot guruhdagi barcha xabarlarni ko'rishi uchun <b>@BotFather</b> ga kiring:\n"
        "1. <code>/mybots</code> -> botingizni tanlang.\n"
        "2. <b>Bot Settings</b> -> <b>Group Privacy</b> -> <b>Turn off</b> qiling.\n\n"
        "🔹 <b>Admin buyruqlari:</b>\n"
        "• <code>/admin</code> - Tugmali admin panelini ochish.\n"
        "• <code>/stats</code> - Obunachilar, guruhlar va so'zlar statistikasi.\n"
        "• <code>/groups</code> - Bot qo'shilgan guruhlar va adminlik holati.\n"
        "• <code>/add exact | kalit_so'z | javob</code> - Aniq mos kelganda javob berish.\n"
        "• <code>/add contains | ibora | javob</code> - Matn ichida uchrashganda javob berish.\n"
        "• <code>/del kalit_so'z</code> - Kalit so'zni o'chirish."
    )
    await message.reply(text, parse_mode="HTML")

import logging
logger = logging.getLogger(__name__)

@private_router.message(F.text)
async def handle_private_message(message: Message, bot: Bot):
    """Shaxsiy chatdagi xabarlarga javob qaytarish."""
    db.add_user(message.from_user.id)
    text = message.text.strip()
    if not text or text.startswith("/"):
        return

    # Shaxsiy chatda botga to'g'ridan-to'g'ri murojaat bo'lgani uchun javob qidiramiz
    response = db.find_response(text, is_mentioned_or_reply=True)
    if not response:
        response = db.get_random_response()

    if response:
        try:
            logger.info(f"💬 Shaxsiy xabar [{message.from_user.full_name}]: '{text}' -> Javob: '{response}'")
            await message.reply(response)
        except Exception as e:
            logger.error(f"Shaxsiy xabar yuborishda xatolik: {e}")
