from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Разместить вакансию", callback_data="vacancy"
    ))
    kb.add(InlineKeyboardButton(
        text="Разместить рекламу", callback_data="ad"
    ))
    kb.add(InlineKeyboardButton(
        text="Управление ботом", callback_data="bot_management"
    ))
    kb.adjust(1)
    return kb.as_markup()


def add_channel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Список каналов", callback_data="channels"
    ))
    kb.adjust(1)
    return kb.as_markup()


def channels_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Изменить цены", callback_data="edit_channel_price"
    ))
    kb.add(InlineKeyboardButton(
        text="Удалить канал", callback_data="del_channel"
    ))
    kb.adjust(1)
    return kb.as_markup()


def bot_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Отправить сообщение во все каналы", callback_data="msg_all_channels"
    ))
    kb.add(InlineKeyboardButton(
        text="Список каналов", callback_data="channels"
    ))
    kb.adjust(1)
    return kb.as_markup()


def sch_admin_final_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Список запланированных сообщений", callback_data="sch_list"
    ))
    kb.add(InlineKeyboardButton(
        text="Управление ботом", callback_data="bot_management"
    ))
    kb.adjust(1)
    return kb.as_markup()


def photo_adm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Без фото", callback_data="without_photo_adm"
    ))
    kb.adjust(1)
    return kb.as_markup()


def end_scheduled_kb(data) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text="Подтвердить", callback_data="sch_confirm_all_msgs"
    ))
    kb.add(InlineKeyboardButton(
        text="Изменить текст", callback_data="edit_sch_text_adm"
    ))
    if 'photo' in data:
        kb.add(InlineKeyboardButton(
            text="Поменять фото", callback_data="edit_sch_photo_adm"
        ))
    kb.add(InlineKeyboardButton(
        text="Изменить дату и время", callback_data="edit_sch_datetime"
    ))
    kb.adjust(1)
    return kb.as_markup()

