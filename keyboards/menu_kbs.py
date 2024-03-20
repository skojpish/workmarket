from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Разместить вакансию", callback_data="vacancy"
    ))
    kb.add(InlineKeyboardButton(
        text="Разместить рекламу", callback_data="ad"
    ))
    kb.adjust(1)
    return kb.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Вернуться в главное меню", callback_data="back_to_menu"
    ))
    kb.adjust(1)
    return kb.as_markup()
