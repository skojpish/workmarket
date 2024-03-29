from aiogram.filters.callback_data import CallbackData


class ChannelCountryCF(CallbackData, prefix='c'):
    channel_id: int
    channel_name: str
    country: str


class ChannelNewCountryCF(CallbackData, prefix='cn'):
    channel_id: int
    channel_name: str


class MsgAllChannelsCF(CallbackData, prefix='mac'):
    country: str


class UserCityCF(CallbackData, prefix='uci'):
    all: bool


class UserCityStatusCF(CallbackData, prefix='ca'):
    add: bool = False
    next: bool = False


class PinCF(CallbackData, prefix='p'):
    pin: bool
    format: str


class YouMoneyCheckCF(CallbackData, prefix='ym'):
    msg_id: int


class TimePickerCF(CallbackData, prefix='tp'):
    up_hour: bool = False
    down_hour: bool = False
    up_min: bool = False
    down_min: bool = False
    confirm: bool = False
    value: int = 0
    hour_cur: int = 0
    minute_cur: int = 0


class EditPriceCF(CallbackData, prefix='ep'):
    cat: str
    channel_name: str
