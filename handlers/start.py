from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.keyboards import main_menu_kb, back_kb
from services.sheets import get_user_by_phone, save_telegram_id

router = Router()


class RegState(StatesGroup):
    phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    # Перевіряємо чи вже є телефон у стані
    data = await state.get_data()
    if data.get("phone"):
        user = get_user_by_phone(data["phone"])
        if user:
            await message.answer(
                f"👋 З поверненням, <b>{user['name']}</b>!\nОберіть дію 👇",
                reply_markup=main_menu_kb()
            )
            return

    await message.answer(
        "👋 Привіт! Ласкаво просимо до <b>EduBot Навчального Центру</b> 🎓\n\n"
        "Для початку введіть ваш номер телефону, яким ви зареєстровані у центрі:\n\n"
        "<i>Приклад: +380971234567</i>"
    )
    await state.set_state(RegState.phone)


@router.message(RegState.phone)
async def handle_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    user = get_user_by_phone(phone)

    if not user:
        await message.answer(
            "❌ Номер телефону <b>не знайдено</b> в базі учнів.\n\n"
            "Перевірте номер або зверніться до адміністратора.\n\n"
            "Спробуйте ще раз:"
        )
        return

    await state.update_data(phone=phone, name=user["name"])
    save_telegram_id(phone, message.from_user.id)
    await state.set_state(None)
    await message.answer(
        f"✅ Вітаємо, <b>{user['name']}</b>!\n\n"
        f"Ви успішно увійшли. Оберіть дію 👇",
        reply_markup=main_menu_kb()
    )


@router.message(Command("menu"))
async def show_menu(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("Головне меню:", reply_markup=main_menu_kb())


@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.message.edit_text("Головне меню — оберіть дію 👇")
    await callback.answer()
