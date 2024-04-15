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
        text="Изменить текст", callback_data="edit_sch_text_user"
    ))
    if 'photo' in data:
        kb.add(InlineKeyboardButton(
            text="Поменять фото", callback_data="edit_sch_photo_user"
        ))
    kb.add(InlineKeyboardButton(
        text="Изменить дату и время", callback_data="edit_sch_datetime"
    ))
    kb.adjust(1)
    return kb.as_markup()


def edit_final_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Перейти к заявке", callback_data="back_to_order"
    ))
    kb.adjust(1)
    return kb.as_markup()


def edit_posts_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Отредактировать содержание публикации", callback_data="edit_post"
    )
    kb.adjust(1)
    return kb.as_markup()


def channel_msg_links_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="🌏СЕТЬ КАНАЛОВ↗️", url='https://t.me/workmarket_goroda'
    ))
    kb.add(InlineKeyboardButton(
        text="📩РАЗМЕСТИТЬ ПУБЛИКАЦИЮ↗️", url='https://t.me/WorkMarketsBot'
    ))
    kb.adjust(1)
    return kb.as_markup()
