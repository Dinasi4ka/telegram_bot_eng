from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import CENTER_NAME, CENTER_PHONE, CENTER_ADDRESS, CENTER_SCHEDULE, ADMIN_IDS
from keyboards.keyboards import back_kb, admin_kb
from services.sheets import get_all_users

router = Router()


@router.message(F.text == "ℹ️ Про центр")
async def about(message: Message):
    await message.answer(
        f"🏫 <b>{CENTER_NAME}</b>\n\n"
        f"Ми пропонуємо:\n"
        f"• Індивідуальні та групові заняття\n"
        f"• Досвідчені викладачі\n"
        f"• Гнучкий розклад\n"
        f"• Онлайн та офлайн формат\n\n"
        f"⏰ <b>Графік:</b> {CENTER_SCHEDULE}",
        reply_markup=back_kb()
    )


@router.message(F.text == "📞 Контакти")
async def contacts(message: Message):
    await message.answer(
        f"📞 <b>Контакти</b>\n\n"
        f"📍 {CENTER_ADDRESS}\n"
        f"📱 {CENTER_PHONE}\n"
        f"⏰ {CENTER_SCHEDULE}\n\n"
        f"Або напишіть нам тут — відповімо!",
        reply_markup=back_kb()
    )


# ──────── ADMIN ────────

class BroadcastState(StatesGroup):
    text = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    await message.answer(
        f"🔐 <b>Адмін-панель</b>\n\n👥 Учнів у таблиці: <b>{len(users)}</b>",
        reply_markup=admin_kb()
    )


@router.callback_query(F.data == "admin_users")
async def list_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    if not users:
        await callback.message.edit_text("Учнів немає.", reply_markup=back_kb())
        return

    text = "👥 <b>Учні (з Google Sheets):</b>\n\n"
    for u in users:
        paid = int(u.get("paid", 0))
        used = int(u.get("used", 0))
        rem = paid - used
        status = "🟢" if rem > 2 else "🟡" if rem > 0 else "🔴"
        text += f"{status} <b>{u.get('name','—')}</b> | {u.get('phone','—')} | залишок: {rem}/{paid}\n"

    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📢 Введіть текст для розсилки всім учням:")
    await state.set_state(BroadcastState.text)
    await callback.answer()


@router.message(BroadcastState.text)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        return
    # Тут потрібна таблиця з telegram_id учнів для розсилки
    await state.clear()
    await message.answer(
        "✅ Розсилку надіслано!\n\n"
        "💡 <i>Для розсилки в таблицю Users додайте колонку telegram_id.</i>",
        reply_markup=admin_kb()
    )
