from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import main_menu_kb, back_kb
from services.sheets import get_user_by_phone
from utils.responses import no_user, no_balance


router = Router()


@router.message(F.text == "💳 Мій баланс")
async def show_balance(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")

    if not phone:
        await message.answer(
            "⚠️ Спочатку введіть ваш номер телефону — надішліть /start"
        )
        return

    user = get_user_by_phone(phone)

    if not user:
        await message.answer(no_user())
        return

    def safe_int(value):
        try:
            return int(value or 0)
        except:
            return 0

    paid = safe_int(user.get("paid"))
    used = safe_int(user.get("used"))

    if paid == 0:
        await message.answer(no_balance())
        return

    remaining = paid - used


    # Візуальна шкала занять
    bar = _progress_bar(used, paid)

    status_emoji = "🟢" if remaining > 2 else "🟡" if remaining > 0 else "🔴"
    status_text = "Все добре" if remaining > 2 else "Скоро закінчиться" if remaining > 0 else "Заняття закінчились!"

    await message.answer(
        f"💳 <b>Ваш баланс занять</b>\n\n"
        f"👤 Учень: <b>{user['name']}</b>\n"
        f"📱 Телефон: <code>{phone}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ Оплачено занять: <b>{paid}</b>\n"
        f"📖 Пройдено занять: <b>{used}</b>\n"
        f"🎯 Залишилось: <b>{remaining}</b> з {paid}\n\n"
        f"{bar}\n\n"
        f"{status_emoji} Статус: <b>{status_text}</b>\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
        + (
            f"⚠️ <i>Залишилось мало занять. Зверніться до викладача для поповнення.</i>"
            if remaining <= 2 else
            f"💡 <i>Для поповнення занять зверніться до викладача.</i>"
        ),
        reply_markup=back_kb()
    )


def _progress_bar(used: int, total: int, length: int = 10) -> str:
    if total == 0:
        return "▱" * length
    filled = round((used / total) * length)
    filled = min(filled, length)
    empty = length - filled
    return "▰" * filled + "▱" * empty + f"  {used}/{total}"
