from aiogram.filters.callback_data import CallbackData


class ChannelCountryCF(CallbackData, prefix='c'):
    channel: int
    country: str


class ChannelNewCountryCF(CallbackData, prefix='cn'):
    channel: int


class MsgAllChannelsCF(CallbackData, prefix='mac'):
    country: str


class UserCityCF(CallbackData, prefix='uci'):
    all: bool


class UserCityStatusCF(CallbackData, prefix='ca'):
    add: bool = False
    next: bool = False


class AdminCityCF(CallbackData, prefix='aci'):
    all: bool


class AdminCityStatusCF(CallbackData, prefix='acs'):
    add: bool = False
    next: bool = False


class PinCF(CallbackData, prefix='p'):
    pin: bool
    format: str


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


class ListOfChannelsCF(CallbackData, prefix='loc'):
    starting_point: int = 0


class EditPostCF(CallbackData, prefix='ep'):
    msg_id: int
    text: bool = False
    photo: bool = False
