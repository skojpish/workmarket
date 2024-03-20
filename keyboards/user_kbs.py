from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def example_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Посмотреть образец", callback_data="example"
    ))
    kb.adjust(1)
    return kb.as_markup()


def back_user_text_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Назад", callback_data="user_text_back"
    ))
    kb.adjust(1)
    return kb.as_markup()


def photo_user_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Без фото", callback_data="without_photo_user"
    ))
    kb.adjust(1)
    return kb.as_markup()


def end_scheduled_user_kb(data) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Оплатить и разместить", callback_data="payment_methods"
    ))
    kb.add(InlineKeyboardButton(
        text="Изменить текст", callback_data="edit_sch_text"
    ))
    if 'photo' in data:
        kb.add(InlineKeyboardButton(
            text="Поменять фото", callback_data="edit_sch_photo"
        ))
    kb.add(InlineKeyboardButton(
        text="Изменить дату и время", callback_data="edit_sch_datetime"
    ))
    kb.adjust(1)
    return kb.as_markup()
