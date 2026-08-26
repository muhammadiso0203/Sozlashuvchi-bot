import logging
import random
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from database import db

logger = logging.getLogger(__name__)
group_router = Router(name="group_router")
group_router.message.filter(F.chat.type != "private")

# Bot guruhga qo'shilganda yoki chiqarilganda kuzatish
@group_router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def bot_joined_group(event: ChatMemberUpdated, bot: Bot):
    """Bot yangi guruhga qo'shilganda."""
    db.add_group(event.chat.id)
    logger.info(f"Bot guruhga qo'shildi: {event.chat.title} (ID: {event.chat.id})")
    try:
        bot_info = await bot.get_me()
        text = (
            f"Assalomu alaykum, <b>{event.chat.title}</b> ahli! 👋\n\n"
            "🤖 <b>Men sizlarning yangi suhbatdosh botingizman!</b>\n\n"
            "Guruhdagi xabarlarga javob qaytarib, suhbatingizni qizitib turaman 😊\n"
            f"Meni chaqirish uchun <code>@{bot_info.username}</code> deb yozishingiz yoki xabarimga reply qilishingiz mumkin."
        )
        await bot.send_message(event.chat.id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Guruhga salom xabari yuborishda xatolik: {e}")

@group_router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def bot_left_group(event: ChatMemberUpdated):
    """Bot guruhdan chiqarilganda yoki chiqqanda."""
    db.remove_group(event.chat.id)
    logger.info(f"Bot guruhdan chiqdi: {event.chat.title} (ID: {event.chat.id})")

# Guruhda /start bosilganda
@group_router.message(CommandStart())
async def handle_group_start(message: Message, bot: Bot):
    """Guruhda /start bosilganda salomlashish."""
    db.add_group(message.chat.id)
    bot_info = await bot.get_me()
    text = (
        f"Assalomu alaykum, <b>{message.chat.title or 'guruh ahli'}</b>! 👋\n\n"
        "🤖 <b>Men guruhda suhbatlashuvchi aqlli botman!</b>\n\n"
        "Guruh a'zolari yozgan xabarlarga avtomatik javob berib turaman 😊\n"
        f"Meni chaqirish uchun <code>@{bot_info.username}</code> deb yozishingiz yoki xabarlarimga reply qilishingiz mumkin."
    )
    await message.reply(text, parse_mode="HTML")

# Guruhdagi matnli xabarlarni tutish
@group_router.message(F.text)
async def handle_group_message(message: Message, bot: Bot):
    # Botning o'zini tekshirish (o'zining xabarlariga o'zi javob bermasligi uchun)
    bot_info = await bot.get_me()
    if message.from_user and message.from_user.id == bot_info.id:
        return

    # Guruh egasi yoki admin anonim / guruh nomidan yozganda Telegram 'GroupAnonymousBot' (1087968824) yoki 'Channel_Bot' (136817688) deb beradi
    ANONYMOUS_BOT_IDS = {1087968824, 136817688, 777000}
    if message.from_user and message.from_user.is_bot and message.from_user.id not in ANONYMOUS_BOT_IDS:
        return

    # Guruhni bazaga kiritib qo'yamiz
    db.add_group(message.chat.id)

    text = message.text.strip()
    if not text:
        return

    user_disp_name = message.from_user.full_name if message.from_user else "Guruh a'zosi"
    logger.info(f"📩 Guruhdan xabar [{message.chat.title}]: '{text}' (Yozuvchi: {user_disp_name})")

    bot_username = f"@{bot_info.username}".lower() if bot_info.username else ""
    
    is_mentioned = False
    is_reply_to_bot = False

    # 1. @bot_username bilan chaqirilganmi?
    if bot_username and bot_username in text.lower():
        is_mentioned = True
        text_clean = text.lower().replace(bot_username, "").strip()
    else:
        text_clean = text

    # 2. Bot yuborgan xabarga reply qilinganmi?
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == bot_info.id:
            is_reply_to_bot = True

    is_direct_interaction = is_mentioned or is_reply_to_bot

    # Kalit so'z yoki murojaat bo'yicha javob qidirish
    response = db.find_response(text_clean, is_mentioned_or_reply=is_direct_interaction)

    # Agar aniq kalit so'z topilmasa va komanda bo'lmasa,
    # 10% ehtimollik bilan bot o'z-o'zidan suhbatga tasodifiy javob bilan qo'shiladi
    if not response and not text.startswith("/"):
        if random.random() < 0.10:  # 10% ehtimollik
            response = db.get_random_response()

    if response:
        try:
            logger.info(f"💬 Guruh xabari: '{text}' -> Javob yuborildi: '{response}'")
            await message.reply(response)
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")
    else:
        logger.info(f"👀 Guruh xabari: '{text}' -> Mos javob topilmadi (ehtimollik tushmadi)")
