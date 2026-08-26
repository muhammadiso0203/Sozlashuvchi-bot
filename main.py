import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import admin_router, private_router, group_router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Xatolik: .env faylida BOT_TOKEN ko'rsatilmagan! Iltimos, @BotFather dan olingan tokenni .env fayliga kiriting.")
        return

    # Bot va Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Outer middleware - barcha kelgan xabarlarni to'liq log qilish
    @dp.message.outer_middleware()
    async def global_message_logger(handler, event: Message, data):
        chat_name = event.chat.title or event.chat.full_name or "Noma'lum"
        user_name = event.from_user.full_name if event.from_user else "Noma'lum"
        logger.info(f"📥 [YANGI XABAR] Chat: '{chat_name}' ({event.chat.type}) | Kimdan: '{user_name}' | Matn: '{event.text}'")
        return await handler(event, data)

    # Routerlarni ulash
    dp.include_router(admin_router)
    dp.include_router(private_router)
    dp.include_router(group_router)

    try:
        bot_info = await bot.get_me()
        logger.info(f"🚀 Bot ishga tushdi: @{bot_info.username} (ID: {bot_info.id})")
        
        # Eski kutilayotgan yangilanishlarni tozalash va pollingni boshlash
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
