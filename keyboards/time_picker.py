from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callback_factories import TimePickerCF


def time_picker_kb(hour, minute) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f"↑", callback_data=TimePickerCF(up_hour=True, down_hour=False, up_min=False, down_min=False,
                                              confirm=False, value=1, hour_cur=hour, minute_cur=minute)
            )
    kb.button(
        text=f"↑", callback_data=TimePickerCF(up_hour=False, down_hour=False, up_min=True, down_min=False,
                                              confirm=False, value=5, hour_cur=hour, minute_cur=minute)
            )
    kb.button(text=f"{hour:02}", callback_data='never')
    kb.button(text=f"{minute:02}", callback_data='never')
    kb.button(
        text=f"↓", callback_data=TimePickerCF(up_hour=False, down_hour=True, up_min=False, down_min=False,
                                              confirm=False, value=1, hour_cur=hour, minute_cur=minute)
             )
    kb.button(
        text=f"↓", callback_data=TimePickerCF(up_hour=False, down_hour=False, up_min=False, down_min=True,
                                              confirm=False, value=5, hour_cur=hour, minute_cur=minute)
             )
    kb.button(text=f"Подтвердить", callback_data=TimePickerCF(up_hour=False, down_hour=False, up_min=False,
                                                              down_min=False, confirm=True, value=0, hour_cur=hour,
                                                              minute_cur=minute)
              )
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()
