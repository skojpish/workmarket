from aiogram.fsm.state import StatesGroup, State


class AddChannel(StatesGroup):
    country = State()
    city = State()
    price_vac = State()
    price_ad = State()


class DelChannel(StatesGroup):
    state = State()


class EditChannel(StatesGroup):
    name = State()
    price_vac = State()
    price_ad = State()


class MsgAllChannels(StatesGroup):
    text = State()
    photo = State()


class UserText(StatesGroup):
    pin_day = State()
    pin_week = State()
    pin_month = State()
    text = State()
    photo = State()


class UserCities(StatesGroup):
    city = State()
