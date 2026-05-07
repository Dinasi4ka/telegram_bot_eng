from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(
        KeyboardButton(text="💳 Мій баланс"),
        KeyboardButton(text="📋 Мій розклад"),
    )
    b.row(
        KeyboardButton(text="❌ Скасувати заняття"),
        KeyboardButton(text="🔄 Перенести заняття"),
    )
    b.row(
        KeyboardButton(text="🛒 Придбати заняття"),
        KeyboardButton(text="ℹ️ Інформація"),
    )
    b.row(
        KeyboardButton(text="👩‍🏫 Написати викладачу"),
    )
    return b.as_markup(resize_keyboard=True)


def back_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="◀️ Назад до меню", callback_data="back")
    return b.as_markup()


def teacher_kb(teacher_link: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✍️ Написати викладачу", url=teacher_link)
    b.button(text="◀️ Назад до меню", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def cancel_lesson_kb(teacher_link: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✍️ Написати викладачу", url=teacher_link)
    b.button(text="◀️ Назад до меню", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def reschedule_kb(teacher_link: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✍️ Написати викладачу", url=teacher_link)
    b.button(text="◀️ Назад до меню", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def packages_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📦 4 заняття — 1400 грн", callback_data="buy:4")
    b.button(text="📦 8 занять — 2800 грн", callback_data="buy:8")
    b.button(text="◀️ Назад до меню", callback_data="back")
    b.adjust(1)
    return b.as_markup()


def payment_kb(link: str, package: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=f"💳 Оплатити {package}", url=link)
    b.button(text="◀️ Назад", callback_data="back_to_packages")
    b.adjust(1)
    return b.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="👥 Всі учні", callback_data="admin_users")
    b.button(text="📢 Розсилка", callback_data="admin_broadcast")
    b.adjust(2)
    return b.as_markup()
