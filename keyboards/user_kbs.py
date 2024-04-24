from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callback_factories import TimePickerCF


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


def channel_msg_links_kb(country) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="🌏СЕТЬ КАНАЛОВ↗️", url='https://t.me/workmarket_goroda'
    ))
    if country == "Россия":
        kb.add(InlineKeyboardButton(
            text="📩РАЗМЕСТИТЬ ПУБЛИКАЦИЮ↗️", url='https://t.me/WorkMarketsBot'
        ))
    elif country == "Беларусь":
        kb.add(InlineKeyboardButton(
            text="📩РАЗМЕСТИТЬ ПУБЛИКАЦИЮ↗️", url='https://t.me/Workmarket_rb_bot'
        ))
    else:
        pass
    kb.adjust(1)
    return kb.as_markup()


def package_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Подтвердить и оплатить", callback_data="payment_methods"
    )
    kb.button(
        text="Назад", callback_data="buy_package"
    )
    kb.adjust(1)
    return kb.as_markup()


def pin_package_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Подтвердить и оплатить", callback_data="payment_methods"
    )
    kb.adjust(1)
    return kb.as_markup()


def time_manually_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Назад", callback_data="time_back"
    )
    kb.adjust(1)
    return kb.as_markup()


def time_manually_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Подтвердить", callback_data=TimePickerCF(up_hour=False, down_hour=False, up_min=False,
                                                       down_min=False, confirm=True, value=0, hour_cur=0,
                                                       minute_cur=0)
    )
    kb.button(
        text="Ввести другое время", callback_data="time_back"
    )
    kb.adjust(1)
    return kb.as_markup()
