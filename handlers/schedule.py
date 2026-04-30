from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import free_slots_kb, confirm_book_kb, my_lessons_kb, confirm_cancel_kb, back_kb
from services.sheets import get_free_slots, book_slot, get_booked_slots_by_phone, unbook_slot_by_phone_and_slot, get_user_by_phone

router = Router()


# ──────────────── Вільні слоти ────────────────

@router.message(F.text == "📅 Вільні заняття")
async def show_free_slots(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("phone"):
        await message.answer("⚠️ Спочатку введіть телефон — /start")
        return

    slots = get_free_slots()
    if not slots:
        await message.answer(
            "📅 <b>Вільних занять наразі немає</b>\n\n"
            "Адміністратор додасть нові слоти найближчим часом.\n"
            "Спробуйте пізніше або зателефонуйте нам.",
            reply_markup=back_kb()
        )
        return

    await message.answer(
        f"📅 <b>Вільні слоти для запису</b>\n\n"
        f"Знайдено вільних занять: <b>{len(slots)}</b>\n"
        f"Оберіть зручний час 👇",
        reply_markup=free_slots_kb(slots)
    )


@router.callback_query(F.data.startswith("book:"))
async def pre_confirm_booking(callback: CallbackQuery, state: FSMContext):
    _, row, date, time = callback.data.split(":", 3)
    data = await state.get_data()
    user = get_user_by_phone(data.get("phone", ""))

    paid = int(user.get("paid", 0)) if user else 0
    used = int(user.get("used", 0)) if user else 0
    remaining = paid - used

    if remaining <= 0:
        await callback.message.edit_text(
            "❌ <b>Недостатньо оплачених занять</b>\n\n"
            "У вас закінчились оплачені заняття.\n"
            "Зверніться до адміністратора для поповнення.",
            reply_markup=back_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📋 <b>Підтвердження запису</b>\n\n"
        f"📆 Дата: <b>{date}</b>\n"
        f"🕐 Час: <b>{time}</b>\n\n"
        f"🎯 Залишок занять після запису: <b>{remaining - 1}</b>\n\n"
        f"Підтвердити?",
        reply_markup=confirm_book_kb(int(row), date, time)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_book:"))
async def do_booking(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":", 3)
    row, date, time = int(parts[1]), parts[2], parts[3]

    data = await state.get_data()
    phone = data.get("phone")

    book_slot(row, phone)

    await callback.message.edit_text(
        f"🎉 <b>Ви успішно записані!</b>\n\n"
        f"📆 Дата: <b>{date}</b>\n"
        f"🕐 Час: <b>{time}</b>\n\n"
        f"Чекаємо вас! Якщо виникнуть зміни — скасуйте або перенесіть через меню.",
        reply_markup=back_kb()
    )
    await callback.answer("Записано ✅")


# ──────────────── Мої заняття ────────────────

@router.message(F.text == "📋 Мої заняття")
async def my_lessons(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    if not phone:
        await message.answer("⚠️ Спочатку введіть телефон — /start")
        return

    lessons = get_booked_slots_by_phone(phone)
    if not lessons:
        await message.answer(
            "📋 <b>У вас немає запланованих занять</b>\n\n"
            "Записатись можна через <b>📅 Вільні заняття</b>",
            reply_markup=back_kb()
        )
        return

    await message.answer(
        f"📋 <b>Ваші заплановані заняття</b> ({len(lessons)}):",
        reply_markup=my_lessons_kb(lessons)
    )


# ──────────────── Скасування ────────────────

@router.message(F.text == "❌ Скасувати заняття")
async def cancel_start(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    if not phone:
        await message.answer("⚠️ Спочатку введіть телефон — /start")
        return

    lessons = get_booked_slots_by_phone(phone)
    if not lessons:
        await message.answer(
            "❌ <b>Немає занять для скасування</b>\n\nУ вас немає запланованих занять.",
            reply_markup=back_kb()
        )
        return

    await message.answer(
        "❌ <b>Оберіть заняття для скасування:</b>",
        reply_markup=my_lessons_kb(lessons)
    )


@router.callback_query(F.data.startswith("cancel_select:"))
async def confirm_cancel(callback: CallbackQuery):
    _, date, time = callback.data.split(":", 2)
    await callback.message.edit_text(
        f"❌ <b>Скасувати заняття?</b>\n\n"
        f"📆 Дата: <b>{date}</b>\n"
        f"🕐 Час: <b>{time}</b>\n\n"
        f"ℹ️ <i>Слот знову стане вільним для інших учнів.</i>",
        reply_markup=confirm_cancel_kb(date, time)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel:"))
async def do_cancel(callback: CallbackQuery, state: FSMContext):
    _, date, time = callback.data.split(":", 2)
    data = await state.get_data()
    phone = data.get("phone")

    success = unbook_slot_by_phone_and_slot(date, time, phone)
    if success:
        await callback.message.edit_text(
            f"✅ <b>Заняття скасовано</b>\n\n"
            f"📆 {date} о {time}\n\n"
            f"Слот звільнено. Ви можете записатись на інший час.",
            reply_markup=back_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Не вдалося скасувати. Зверніться до адміністратора.",
            reply_markup=back_kb()
        )
    await callback.answer()
