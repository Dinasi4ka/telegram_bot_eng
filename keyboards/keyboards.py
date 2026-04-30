from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="💳 Мій баланс"),
          KeyboardButton(text="📅 Вільні заняття"))
    b.row(KeyboardButton(text="📋 Мої заняття"),
          KeyboardButton(text="❌ Скасувати заняття"))
    b.row(KeyboardButton(text="ℹ️ Про центр"),
          KeyboardButton(text="📞 Контакти"))
    return b.as_markup(resize_keyboard=True)


def free_slots_kb(slots: list[dict]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in slots:
        label = f"📆 {s['date']}  🕐 {s['time']}"
        b.button(text=label, callback_data=f"book:{s['row']}:{s['date']}:{s['time']}")
    b.button(text="◀️ Назад", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def confirm_book_kb(row: int, date: str, time: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Підтвердити запис", callback_data=f"confirm_book:{row}:{date}:{time}")
    b.button(text="❌ Скасувати", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def my_lessons_kb(lessons: list[dict]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for l in lessons:
        label = f"📆 {l['date']}  🕐 {l['time']}"
        b.button(text=label, callback_data=f"cancel_select:{l['date']}:{l['time']}")
    b.button(text="◀️ Назад", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def confirm_cancel_kb(date: str, time: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Так, скасувати", callback_data=f"confirm_cancel:{date}:{time}")
    b.button(text="◀️ Ні, залишити", callback_data="back")
    b.adjust(2)
    return b.as_markup()


def back_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="◀️ Назад до меню", callback_data="back")
    return b.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="👥 Всі учні", callback_data="admin_users")
    b.button(text="📢 Розсилка", callback_data="admin_broadcast")
    b.adjust(2)
    return b.as_markup()
