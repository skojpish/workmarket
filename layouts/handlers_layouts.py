from datetime import timedelta, datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import bot
from database.FSM import UserCities, AdminCities
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from handlers.callback_factories import UserCityCF, AdminCityCF
from keyboards.admin_kbs import end_scheduled_kb
from keyboards.user_kbs import end_scheduled_user_kb


async def start_message_lo(msg, state, kb):
    await state.clear()
    message = await msg.answer(f"Здравствуйте, {msg.from_user.full_name}!\n\n"
                     f"Этот бот поможет Вам разместить вакансию или рекламу в сети телеграм каналов Workmarket.",
                     reply_markup=kb())
    await bot.delete_message(msg.from_user.id, msg.message_id)
    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


async def del_messages_lo(user_id):
    messages = await DelMsgsQs.get_msgs(user_id)
    for message in messages:
        try:
            await bot.delete_message(user_id, message)
        except Exception:
            pass

    await DelMsgsQs.del_msgs_id(user_id)


async def choice_user_first_city(callback, state, cat):
    data = await state.get_data()

    if 'cities' in data:
        cities_all = await ChannelsQs.get_cities(cat)
        user_cities = data['cities'].split()
        cities = [(city[0], city[1]) for city in cities_all if city[0] not in user_cities]
    else:
        cities = await ChannelsQs.get_cities(cat)

    if 'cat' not in data:
        await state.update_data(cat=cat)

    prices = []

    for price in cities:
        prices.append(price[1])

    def city_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Во всех городах ({sum(prices)} руб.)", callback_data=UserCityCF(
                all=True)
        )
        kb.adjust(1)
        return kb.as_markup()

    new_line = '\n'

    await state.set_state(UserCities.city)

    if cities:
        await callback.message.edit_text(f"Напишите название города из списка представленного ниже:\n\n"
                                         f"{new_line.join(f'{cities.index(city)+1}. {city[0]} ({city[1]} руб.)' for city in cities)}")
        await callback.message.edit_reply_markup(reply_markup=city_kb())
    else:
        await callback.answer()


async def choice_admin_city(callback, state, country):
    data = await state.get_data()

    if 'cities' in data:
        cities_all = await ChannelsQs.get_cities_admin(country)
        user_cities = data['cities'].split()
        cities = [city for city in cities_all if city not in user_cities]
    else:
        cities = await ChannelsQs.get_cities_admin(country)

    def city_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Во всех городах", callback_data=AdminCityCF(
                all=True)
        )
        kb.adjust(1)
        return kb.as_markup()

    new_line = '\n'

    await state.set_state(AdminCities.city)

    if cities:
        await callback.message.edit_text(f"Напишите название города из списка представленного ниже:\n\n"
                                         f"{new_line.join(f'{cities.index(city)+1}. {city}' for city in cities)}")
        await callback.message.edit_reply_markup(reply_markup=city_kb())
    else:
        await callback.answer()


async def order_message_lo(callback, state, data):
    await callback.answer()

    message_photo = None

    if data['role'] == 'admin':
        if 'photo' in data:
            try:
                message = await callback.message.answer_photo(data['photo'], f"Вы ввели следующие данные:\n"
                                                                   f"Сообщение: {data['text']}\n"
                                                                   f"Дата: {data['date_cal']}\n"
                                                                   f"Время: {data['time']}\n\n"
                                                                   f"Города: {data['cities']}",
                                                    reply_markup=end_scheduled_kb(data))
            except TelegramBadRequest:
                message_photo = await callback.message.answer_photo(data['photo'])
                message = await callback.message.answer(f"Вы ввели следующие данные:\n"
                                                                   f"Сообщение: {data['text']}\n"
                                                                   f"Дата: {data['date_cal']}\n"
                                                                   f"Время: {data['time']}\n\n"
                                                                   f"Города: {data['cities']}",
                                                    reply_markup=end_scheduled_kb(data))
        else:
            message = await callback.message.answer(f"Вы ввели следующие данные:\n"
                                                    f"Сообщение: {data['text']}\n"
                                                    f"Дата: {data['date_cal']}\n"
                                                    f"Время: {data['time']}\n\n"
                                                    f"Города: {data['cities']}",
                                          reply_markup=end_scheduled_kb(data))
    else:
        if data['pin']:
            if 'pin_day' in data:
                pin_date = datetime.strptime(data['date_cal'], '%d.%m.%Y') + timedelta(days=data['pin_day'])

                pin = f"до {data['time']} {pin_date.date().strftime('%d.%m.%Y')}"
            elif 'pin_week' in data:
                pin_date = datetime.strptime(data['date_cal'], '%d.%m.%Y') + timedelta(days=data['pin_week'] * 7)

                pin = f"до {data['time']} {pin_date.date().strftime('%d.%m.%Y')}"
            else:
                pin_date = datetime.strptime(data['date_cal'], '%d.%m.%Y') + timedelta(days=data['pin_month'] * 30)

                pin = f"до {data['time']} {pin_date.date().strftime('%d.%m.%Y')}"
            await state.update_data(pin=f"{data['time']} {pin_date.date()}")
        else:
            pin = "Не закреплять"

        if 'photo' in data:
            try:
                message = await callback.message.answer_photo(data['photo'], f"Вы ввели следующие данные:\n\n"
                                                                   f"{data['text']}\n\n"
                                                                   f"Дата: {data['date_cal']}\n"
                                                                   f"Время: {data['time']}\n"
                                                                   f"Закрепление: {pin}\n\n"
                                                                   f"Города: {data['cities']}",
                                                    reply_markup=end_scheduled_user_kb(data))
            except TelegramBadRequest:
                message_photo = await callback.message.answer_photo(data['photo'])
                message = await callback.message.answer(f"Вы ввели следующие данные:\n\n"
                                                                             f"{data['text']}\n\n"
                                                                             f"Дата: {data['date_cal']}\n"
                                                                             f"Время: {data['time']}\n"
                                                                             f"Закрепление: {pin}\n\n"
                                                                             f"Города: {data['cities']}",
                                                              reply_markup=end_scheduled_user_kb(data))
        else:
            message = await callback.message.answer(f"Вы ввели следующие данные:\n\n"
                                          f"{data['text']}\n\n"
                                          f"Дата: {data['date_cal']}\n"
                                          f"Время: {data['time']}\n"
                                          f"Закрепление: {pin}\n\n"
                                          f"Города: {data['cities']}",
                                          reply_markup=end_scheduled_user_kb(data))
    await del_messages_lo(callback.from_user.id)

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)

    if message_photo is not None:
        await DelMsgsQs.add_msg_id(callback.from_user.id, message_photo.message_id)
