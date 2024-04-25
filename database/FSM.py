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
    pin = State()
    text = State()
    photo = State()
    time_manually = State()


class UserCities(StatesGroup):
    city = State()


class AdminCities(StatesGroup):
    city = State()


class EditPost(StatesGroup):
    number = State()
    text = State()
    photo = State()
