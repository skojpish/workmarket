from aiogram.filters.callback_data import CallbackData


class ChannelCountryCF(CallbackData, prefix='c'):
    channel_id: int
    channel_name: str
    country: str


class ChannelNewCountryCF(CallbackData, prefix='cn'):
    channel_id: int
    channel_name: str


class UserCountryCF(CallbackData, prefix='uc'):
    country: str


class UserCityCF(CallbackData, prefix='uci'):
    country: str
    cities: str


class UserCityStatusCF(CallbackData, prefix='ca'):
    add: bool = False
    next: bool = False
    country: str = ''
    cities: str


class PinCF(CallbackData, prefix='p'):
    pin: bool
    format: str
    country: str
    cities: str


class YouMoneyCheckCF(CallbackData, prefix='ym'):
    msg_id: int
