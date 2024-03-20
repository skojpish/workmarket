from aiogram.fsm.state import StatesGroup, State


class AddChannel(StatesGroup):
    country = State()
    city = State()
    price_vac = State()
    price_ad = State()


class DelChannel(StatesGroup):
    state = State()


class MsgAllChannels(StatesGroup):
    date = State()
    time = State()
    text = State()
    photo = State()


class UserText(StatesGroup):
    pin_day = State()
    pin_week = State()
    text = State()
    photo = State()
    date = State()
    time = State()


