from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, TEACHER_USERNAME, TEACHER_LINK, MONOBANK_LINK_4, MONOBANK_LINK_8, PRICE_4, PRICE_8
from keyboards.keyboards import back_kb, admin_kb, packages_kb, payment_kb, teacher_kb
from services.sheets import get_all_users

router = Router()


# ──────────────── Інформація ────────────────

@router.message(F.text == "ℹ️ Інформація")
async def show_info(message: Message):
    await message.answer(
        "ℹ️ <b>Інформація та правила</b>\n\n"
        "📅 <b>Розклад і переноси:</b>\n"
        "• Перенесення можливе до <b>3 разів на місяць</b>\n"
        "• Про перенесення необхідно повідомляти завчасно (щонайменше за 1-1,5 год до початку заняття), інакше заняття буде зняте з балансу\n"
        "• Для зміни розкладу пишіть викладачу\n\n"
        "❌ <b>Скасування:</b>\n"
        "• Без списання — якщо повідомлено <b>за 1 годину</b> до заняття\n"
        "• Якщо пізніше — заняття списується та скасовується\n\n"
        "💰 <b>Оплата та баланс:</b>\n"
        "• Заняття автоматично списується за 1 годину до уроку\n"
        "• Якщо баланс не поповнений — заняття автоматично скасовується за годину до його початку\n"
        "• Якщо ви хочете поновити баланс та заняття - напишіть викладачу. Якщо поповнили баланс запізно( після автоматичного скасування) — обов'язково напишіть викладачу\n\n"
        "📩 <b>Важливо:</b>\n"
        "• Усі зміни розкладу узгоджуються через викладача\n"
        "• Для запитів використовуйте кнопки меню або чат бота",
        reply_markup=back_kb()
    )


# ──────────────── Написати викладачу ────────────────

@router.message(F.text == "👩‍🏫 Написати викладачу")
async def contact_teacher(message: Message):
    await message.answer(
        f"👩‍🏫 <b>Написати викладачу</b>\n\n"
        f"Натисніть кнопку нижче щоб перейти до чату з викладачем:",
        reply_markup=teacher_kb(TEACHER_LINK)
    )


# ──────────────── Придбати заняття ────────────────

@router.message(F.text == "🛒 Придбати заняття")
async def buy_lessons(message: Message):
    await message.answer(
        "🛒 <b>Придбати заняття</b>\n\n"
        "Оберіть пакет занять 👇",
        reply_markup=packages_kb()
    )


@router.callback_query(F.data == "back_to_packages")
async def back_to_packages(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛒 <b>Придбати заняття</b>\n\nОберіть пакет занять 👇",
        reply_markup=packages_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "buy:4")
async def buy_4(callback: CallbackQuery):
    await callback.message.edit_text(
        f"📦 <b>Пакет: 4 заняття</b>\n\n"
        f"💰 Ціна: <b>{PRICE_4} грн</b>\n\n"
        f"Для оплати натисніть кнопку нижче 👇\n\n"
        f"<i>Після оплати обов'язково надішліть скріншот викладачу — {TEACHER_USERNAME}</i>",
        reply_markup=payment_kb(MONOBANK_LINK_4, "4 заняття")
    )
    await callback.answer()


@router.callback_query(F.data == "buy:8")
async def buy_8(callback: CallbackQuery):
    await callback.message.edit_text(
        f"📦 <b>Пакет: 8 занять</b>\n\n"
        f"💰 Ціна: <b>{PRICE_8} грн</b>\n\n"
        f"Для оплати натисніть кнопку нижче 👇\n\n"
        f"<i>Після оплати обов'язково надішліть скріншот викладачу — {TEACHER_USERNAME}</i>",
        reply_markup=payment_kb(MONOBANK_LINK_8, "8 занять")
    )
    await callback.answer()


# ──────────────── ADMIN ────────────────

class BroadcastState(StatesGroup):
    text = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    await message.answer(
        f"🔐 <b>Адмін-панель</b>\n\n👥 Учнів: <b>{len(users)}</b>",
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

    text = "👥 <b>Учні:</b>\n\n"
    for u in users:
        paid = int(u.get("paid", 0) or 0)
        used = int(u.get("used", 0) or 0)
        rem = paid - used
        status = "🟢" if rem > 2 else "🟡" if rem > 0 else "🔴"
        text += f"{status} <b>{u.get('name','—')}</b> | {u.get('phone','—')} | залишок: {rem}/{paid}\n"

    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📢 Введіть текст для розсилки:")
    await state.set_state(BroadcastState.text)
    await callback.answer()


@router.message(BroadcastState.text)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    await state.clear()
    await message.answer(
        f"✅ Розсилку надіслано! ({len(users)} учнів)",
        reply_markup=admin_kb()
    )
