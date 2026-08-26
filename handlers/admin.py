import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from database import db

logger = logging.getLogger(__name__)
admin_router = Router(name="admin_router")

# FSM holatlari (So'z qo'shish va o'chirish uchun)
class AdminStates(StatesGroup):
    waiting_for_add = State()
    waiting_for_del = State()

def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshiradi."""
    return not ADMIN_IDS or user_id in ADMIN_IDS

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli tugmalari."""
    kb = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📋 So'zlar ro'yxati", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton(text="➕ Yangi so'z qo'shish", callback_data="admin_add"),
            InlineKeyboardButton(text="🗑 So'zni o'chirish", callback_data="admin_del")
        ],
        [
            InlineKeyboardButton(text="❌ Menyuni yopish", callback_data="admin_close")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Bekor qilish tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="admin_menu")]
    ])

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Admin panelni ochish."""
    if not is_admin(message.from_user.id):
        await message.reply("⛔️ Kechirasiz, siz admin emassiz.")
        return

    await state.clear()
    text = (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        "Quyidagi tugmalar orqali botdagi so'zlar va javoblarni boshqarishingiz mumkin:"
    )
    await message.reply(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_menu")
async def cb_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Asosiy admin menyuga qaytish."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.clear()
    text = (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        "Quyidagi tugmalar orqali botdagi so'zlar va javoblarni boshqarishingiz mumkin:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await callback.answer()

def format_stats_text() -> str:
    """Statistika matnini formatlash."""
    stats = db.get_stats()
    return (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👤 <b>Obunachilar soni:</b> {stats['users_count']} ta\n"
        f"👥 <b>Guruhlar soni:</b> {stats['groups_count']} ta\n"
        "────────────────────\n"
        f"🔹 <b>Aniq mos keluvchi so'zlar:</b> {stats['exact_keywords']} ta\n"
        f"🔹 <b>Qisman mos keluvchi so'zlar:</b> {stats['contains_keywords']} ta\n"
        f"🔹 <b>Chaqirilgandagi javoblar:</b> {stats['mention_replies']} ta\n"
        f"📌 <b>Jami kalit so'zlar:</b> {stats['total_keywords']} ta"
    )

@admin_router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Baza statistikasini ko'rsatish."""
    if not is_admin(message.from_user.id):
        return

    await message.reply(format_stats_text(), parse_mode="HTML")

@admin_router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Statistika tugmasi."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await callback.message.edit_text(format_stats_text(), reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "admin_list")
async def cb_admin_list(callback: CallbackQuery):
    """Mavjud barcha so'zlar ro'yxati."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    all_words = db.get_all_keywords()
    exact_list = ", ".join(f"<code>{w}</code>" for w in all_words["exact"][:30]) or "Yo'q"
    contains_list = ", ".join(f"<code>{w}</code>" for w in all_words["contains"][:30]) or "Yo'q"

    text = (
        "📋 <b>Bazada mavjud kalit so'zlar:</b>\n\n"
        f"🎯 <b>Aniq moslik (Exact):</b>\n{exact_list}\n\n"
        f"🔍 <b>Qisman moslik (Contains):</b>\n{contains_list}\n\n"
        "<i>(Ko'p bo'lsa dastlabki 30 tasi ko'rsatiladi)</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "admin_add")
async def cb_admin_add(callback: CallbackQuery, state: FSMContext):
    """Yangi so'z qo'shish so'rovi."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_add)
    text = (
        "➕ <b>Yangi so'z qo'shish:</b>\n\n"
        "Quyidagi formatda yozib yuboring:\n"
        "<code>tur | kalit_so'z | javob_matni</code>\n\n"
        "<b>Turlar:</b>\n"
        "• <code>exact</code> - xabar aniq shu so'z bo'lsa\n"
        "• <code>contains</code> - xabar ichida shu so'z qatnashsa\n\n"
        "<b>Misol:</b>\n"
        "<code>exact | xayrli kech | Xayrli kech barchaga!</code>"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminStates.waiting_for_add, F.text)
async def process_add_word(message: Message, state: FSMContext):
    """Admin kiritgan yangi so'zni saqlash."""
    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()
    if "|" not in text:
        await message.reply(
            "⚠️ Noto'g'ri format! Iltimos, <code>tur | kalit_so'z | javob</code> formatida yozing.",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return

    parts = [p.strip() for p in text.split("|", 2)]
    if len(parts) < 3:
        await message.reply(
            "⚠️ 3 ta qism bo'lishi kerak: <code>tur | kalit_so'z | javob</code>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return

    match_type, keyword, response_text = parts
    match_type = match_type.lower()

    if match_type not in ["exact", "contains"]:
        await message.reply(
            "⚠️ Turi faqat <code>exact</code> yoki <code>contains</code> bo'lishi mumkin!",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return

    db.add_keyword_response(match_type, keyword, response_text)
    await state.clear()
    await message.reply(
        f"✅ <b>Muvaffaqiyatli qo'shildi!</b>\n\n"
        f"▫️ <b>Turi:</b> {match_type}\n"
        f"▫️ <b>Kalit so'z:</b> <i>{keyword}</i>\n"
        f"▫️ <b>Javob:</b> <i>{response_text}</i>",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "admin_del")
async def cb_admin_del(callback: CallbackQuery, state: FSMContext):
    """So'zni o'chirish so'rovi."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_del)
    text = (
        "🗑 <b>So'zni o'chirish:</b>\n\n"
        "O'chirmoqchi bo'lgan kalit so'zingizni yozib yuboring.\n"
        "Misol: <code>salom</code>"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminStates.waiting_for_del, F.text)
async def process_del_word(message: Message, state: FSMContext):
    """Admin kiritgan so'zni bazadan o'chirish."""
    if not is_admin(message.from_user.id):
        return

    keyword = message.text.strip()
    deleted = db.remove_keyword(keyword)
    await state.clear()

    if deleted:
        await message.reply(
            f"🗑 <b>'{keyword}'</b> kalit so'zi bazadan o'chirildi.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.reply(
            f"❌ Bazadan <b>'{keyword}'</b> kalit so'zi topilmadi.",
            reply_markup=get_admin_keyboard(),
            parse_mode="HTML"
        )

@admin_router.callback_query(F.data == "admin_close")
async def cb_admin_close(callback: CallbackQuery, state: FSMContext):
    """Menyuni yopish."""
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        await callback.message.edit_text("Admin paneli yopildi.")
    await callback.answer()
