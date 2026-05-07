from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import TEACHER_LINK
from keyboards.keyboards import back_kb, cancel_lesson_kb, reschedule_kb
from services.sheets import get_booked_slots_by_phone
from utils.responses import no_user, no_schedule

router = Router()


@router.message(F.text == "📋 Мій розклад")
async def my_schedule(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    if not phone:
        await message.answer(no_user())
        return

    lessons = get_booked_slots_by_phone(phone)

    if not lessons:
        await message.answer(no_schedule())
        return

    text = "📋 <b>Ваш розклад занять:</b>\n\n"
    for l in sorted(lessons, key=lambda x: (str(x.get("date", "")), str(x.get("time", "")))):
        text += f"📆 <b>{l.get('date', '—')}</b>  🕐 <b>{l.get('time', '—')}</b>\n"

    text += "\nДля змін — зверніться до викладача через кнопку меню."
    await message.answer(text, reply_markup=back_kb())


@router.message(F.text == "❌ Скасувати заняття")
async def cancel_info(message: Message):
    await message.answer(
        "❌ <b>Скасування заняття</b>\n\n"
        "⚠️ <b>Умови:</b>\n"
        "• Без списання заняття — якщо скасування зроблено <b>за 1 годину</b> до уроку\n"
        "• Якщо пізніше — заняття списується і скасовується\n\n"
        "Напишіть викладачу:\n"
        "1️⃣ Дату і час заняття\n"
        "2️⃣ Причину (за бажанням)\n\n"
        "👇 Натисніть кнопку нижче:",
        reply_markup=cancel_lesson_kb(TEACHER_LINK)
    )


@router.message(F.text == "🔄 Перенести заняття")
async def reschedule_info(message: Message):
    await message.answer(
        "🔄 <b>Перенесення заняття</b>\n\n"
        "⚠️ <b>Правила:</b>\n"
        "• Перенесення можливе до <b>3 разів на місяць</b>\n"
        "• Просимо повідомляти завчасно (щонайменше <b>за 1 год</b> до початку заняття)\n\n"
        "Напишіть викладачу:\n"
        "1️⃣ Дату і час заняття\n"
        "2️⃣ На коли зручно перенести (час та дата узгоджується з викладачем)\n\n"
        "👇 Натисніть кнопку нижче:",
        reply_markup=reschedule_kb(TEACHER_LINK)
    )
