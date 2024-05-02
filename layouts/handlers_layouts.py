from datetime import timedelta, datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import bot
from database.FSM import UserCities, AdminCities
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from database.package_pins import PackagePinsQs
from database.package_posts import PackagePostsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import UserCityCF, AdminCityCF, PinCF, UserCityStatusCF, AdminCityStatusCF
from handlers.schedulers import add_package_posts_job, add_package_pins_job
from keyboards.admin_kbs import end_scheduled_kb
from keyboards.time_picker import time_picker_kb
from keyboards.user_kbs import end_scheduled_user_kb


async def start_message_lo(msg, state, kb):
    await state.clear()
    message = await msg.answer(f"Здравствуйте, {msg.from_user.full_name}!\n\n"
                     f"Этот бот поможет Вам разместить вакансию или рекламу по всем городам России 🇷🇺 "
                               f"в сети телеграм каналов Workmarket https://t.me/workmarket_goroda",
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


async def choice_city_lo(callback, state, starting_point):
    data = await state.get_data()
    if 'cities' in data:
        user_cities = data['cities'].split(',')
        cities = await ChannelsQs.get_cities(data['cat'], starting_point, user_cities)
    else:
        cities = await ChannelsQs.get_cities(data['cat'], starting_point, [])

    if 'all_cities_sum' not in data:
        cities_all = await ChannelsQs.get_all_cities(data['cat'])
        prices = []
        for price in cities_all:
            prices.append(price[1])
        await state.update_data(all_cities_sum=sum(prices))

    data = await state.get_data()

    def city_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if len(cities) > 100:
            kb.button(
                text="Показать еще",
                callback_data=UserCityStatusCF(
                        add=True,
                        next=False,
                        starting_point=starting_point+100,
                        back=False
                )
            )
        if starting_point > 0:
            kb.button(
                text="Назад",
                callback_data=UserCityStatusCF(
                        add=True,
                        next=False,
                        starting_point=starting_point-100,
                        back=True
                )
            )
        kb.button(
            text=f"Во всех городах {'{:g}'.format(data['all_cities_sum'] * 0.7)} руб. (скидка 30%)",
            callback_data=UserCityCF(
                all=True)
        )
        kb.button(
            text=f"Пакетное размещение (скидка до 95%)",
            callback_data="packages"
        )
        kb.adjust(1)
        return kb.as_markup()

    new_line = '\n'

    await state.set_state(UserCities.city)

    if cities:
        await callback.message.edit_text(f"{new_line.join(f'{cities.index(city) + 1 + starting_point}. {city[0]} ({city[1]} руб.)' for city in cities[0:100])}\n\n"
                                         f"Напишите название города из списка представленного выше или укажите несколько городов, "
                                         f"где вы хотели бы разместить публикацию, через запятую (после каждой запятой пробел обязателен)\n"
                                         f"Например:\n"
                                         f"Город1, Город2, Город3")
        await callback.message.edit_reply_markup(reply_markup=city_kb())
    else:
        await callback.answer()


async def choice_user_first_city(callback, state, cat, starting_point):
    data = await state.get_data()

    if 'cat' not in data:
        await state.update_data(cat=cat)

    users_pckg_info = await PackagePostsQs.get_user(callback.from_user.id)

    try:
        if users_pckg_info[0] and users_pckg_info[1] == cat:
            await state.update_data(package_posts=True)

            def package_kb() -> InlineKeyboardMarkup:
                kb = InlineKeyboardBuilder()
                kb.button(
                    text=f"Опубликовать во всех городах",
                    callback_data=UserCityCF(
                        all=True)
                )
                kb.adjust(1)
                return kb.as_markup()

            await callback.message.edit_text(f"У вас осталось <b>{users_pckg_info[0]}</b> публикаций во всех городах")
            await callback.message.edit_reply_markup(reply_markup=package_kb())
        else:
            await choice_city_lo(callback, state, starting_point)
    except TypeError:
        await choice_city_lo(callback, state, starting_point)


async def choice_admin_city(callback, starting_point, state, country):
    data = await state.get_data()

    if 'cities' in data:
        admin_cities = data['cities'].split(',')
        cities = await ChannelsQs.get_cities_admin(country, starting_point, admin_cities)
    else:
        cities = await ChannelsQs.get_cities_admin(country, starting_point, [])

    def city_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if len(cities) > 100:
            kb.button(
                text="Показать еще",
                callback_data=AdminCityStatusCF(
                        add=True,
                        next=False,
                        starting_point=starting_point+100,
                        back=False
                )
            )
        if starting_point > 0:
            kb.button(
                text="Назад",
                callback_data=AdminCityStatusCF(
                        add=True,
                        next=False,
                        starting_point=starting_point-100,
                        back=True
                )
            )
        kb.button(
            text=f"Во всех городах", callback_data=AdminCityCF(
                all=True)
        )
        kb.adjust(1)
        return kb.as_markup()

    new_line = '\n'

    await state.set_state(AdminCities.city)

    if cities:
        await callback.message.edit_text(f"{new_line.join(f'{cities.index(city)+1+starting_point}. {city}' for city in cities[0:100])}\n\n"
                                         f"Напишите название города из списка представленного выше или укажите несколько городов, "
                                         f"где вы хотели бы разместить публикацию, через запятую (после каждой запятой пробел обязателен)\n"
                                         f"Например:\n"
                                         f"Город1, Город2, Город3")
        await callback.message.edit_reply_markup(reply_markup=city_kb())
    else:
        await callback.answer()


async def order_message_lo(callback, state, data):
    await callback.answer()

    message_photo = None

    if data['role'] == 'admin':
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
                message = await callback.message.answer_photo(data['photo'], f"Вы ввели следующие данные:\n"
                                                                   f"Сообщение: {data['text']}\n"
                                                                   f"Дата: {data['date_cal']}\n"
                                                                   f"Время: {data['time']}\n"
                                                                   f"Закрепление: {pin}\n\n"
                                                                   f"Города: {data['cities'] if 'all_cities' not in data else data['all_cities']}",
                                                    reply_markup=end_scheduled_kb(data))
            except TelegramBadRequest:
                message_photo = await callback.message.answer_photo(data['photo'])
                message = await callback.message.answer(f"Вы ввели следующие данные:\n"
                                                                   f"Сообщение: {data['text']}\n"
                                                                   f"Дата: {data['date_cal']}\n"
                                                                   f"Время: {data['time']}\n"
                                                                   f"Закрепление: {pin}\n\n"
                                                                   f"Города: {data['cities'] if 'all_cities' not in data else data['all_cities']}",
                                                    reply_markup=end_scheduled_kb(data))
        else:
            message = await callback.message.answer(f"Вы ввели следующие данные:\n"
                                                    f"Сообщение: {data['text']}\n"
                                                    f"Дата: {data['date_cal']}\n"
                                                    f"Время: {data['time']}\n"
                                                    f"Закрепление: {pin}\n\n"
                                                    f"Города: {data['cities'] if 'all_cities' not in data else data['all_cities']}",
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
                                                                   f"Города: {data['cities'] if 'all_cities' not in data else data['all_cities']}",
                                                    reply_markup=end_scheduled_user_kb(data))
            except TelegramBadRequest:
                message_photo = await callback.message.answer_photo(data['photo'])
                message = await callback.message.answer(f"Вы ввели следующие данные:\n\n"
                                                                             f"{data['text']}\n\n"
                                                                             f"Дата: {data['date_cal']}\n"
                                                                             f"Время: {data['time']}\n"
                                                                             f"Закрепление: {pin}\n\n"
                                                                             f"Города: {data['cities'] if 'all_cities' not in data else data['all_cities']}",
                                                              reply_markup=end_scheduled_user_kb(data))
        else:
            message = await callback.message.answer(f"Вы ввели следующие данные:\n\n"
                                          f"{data['text']}\n\n"
                                          f"Дата: {data['date_cal']}\n"
                                          f"Время: {data['time']}\n"
                                          f"Закрепление: {pin}\n\n"
                                          f"Города: {data['cities'] if 'all_cities' not in data else data['all_cities']}",
                                          reply_markup=end_scheduled_user_kb(data))
    await del_messages_lo(callback.from_user.id)

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)

    if message_photo is not None:
        await DelMsgsQs.add_msg_id(callback.from_user.id, message_photo.message_id)


async def confirm_payment_lo(callback, state):
    data = await state.get_data()
    if 'publ_count' in data:
        del_datetime = datetime.now() + timedelta(days=30)
        d = {
            'user_id': callback.from_user.id,
            'publ_count': data['publ_count'],
            'cat': data['cat'],
            'del_datetime': del_datetime
        }
        await callback.message.delete_reply_markup()
        package_data = await PackagePostsQs.add_posts_package(**d)
        await add_package_posts_job(package_data[0], package_data[1])
        await callback.message.edit_text(f"Оплата проведена успешно!\n"
                                         f"Теперь у вас есть возможность опубликовать {data['publ_count']} "
                                         f"постов во всех каналах сети Workmarket до "
                                         f"{del_datetime.strftime('%H:%M %d.%m.%Y')}!")
    elif 'pin_count' in data:
        del_datetime = datetime.now() + timedelta(days=30)
        d = {
            'user_id': callback.from_user.id,
            'pin_count': data['pin_count'],
            'cat': data['cat'],
            'del_datetime': del_datetime
        }
        await callback.message.delete_reply_markup()
        pin_package_data = await PackagePinsQs.add_pins_package(**d)
        await add_package_pins_job(pin_package_data[0], pin_package_data[1])
        await callback.message.edit_text(f"Оплата проведена успешно!\n"
                                         f"Теперь у вас есть возможность использовать {data['pin_count']} "
                                         f"одномесячных закреплений постов в каналах сети Workmarket до "
                                         f"{del_datetime.strftime('%H:%M %d.%m.%Y')}!")
    else:
        date_time = f"{data['date_cal']} {data['time']}"

        d = {
            'user_id': callback.from_user.id,
            'date_time': datetime.strptime(date_time, "%d.%m.%Y %H:%M"),
            'text': data['text'],
            'cities': data['cities']
        }

        if 'photo' in data:
            d['photo'] = data['photo']

        if data['pin']:
            d['pin'] = datetime.strptime(data['pin'], '%H:%M %Y-%m-%d')

        await callback.message.delete_reply_markup()
        await SchMsgsQs.add_sch_msg_user(**d)
        await callback.message.edit_text("Оплата проведена успешно!\n"
                                         "Посмотреть свои запланированные посты можно с помощью команды /posts")


async def pin_lo(callback, cat):
    def pin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Закрепить посуточно", callback_data=PinCF(pin=True,
                                                            format='day')
        )
        kb.button(
            text="Закрепить понедельно", callback_data=PinCF(pin=True,
                                                             format='week')
        )
        kb.button(
            text="Закрепить помесячно", callback_data=PinCF(pin=True,
                                                            format='month')
        )
        kb.button(
            text="Не закреплять", callback_data=PinCF(pin=False,
                                                      format='')
        )
        kb.button(
            text=f"Пакетное закрепление (скидка до 95%)",
            callback_data="packages_pin"
        )
        kb.adjust(1)
        return kb.as_markup()

    if cat == 'vac':
        await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?\n\n"
                                         f"Стоимость размещения с закреплением:\n"
                                         f" + 300 руб./сутки\n"
                                         f" + 1500 руб./неделя\n"
                                         f" + 3000 руб./месяц")
    elif cat == 'ad':
        await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?\n\n"
                                         f"Стоимость размещения с закреплением:\n"
                                         f" + 500 руб./сутки\n"
                                         f" + 2000 руб./неделя\n"
                                         f" + 4000 руб./месяц")
    await callback.message.edit_reply_markup(reply_markup=pin_kb())


async def time_picker_lo(callback, callback_data, state):
    await state.update_data(time=f'{callback_data.hour_cur:02}:{callback_data.minute_cur:02}')
    data = await state.get_data()

    date_time = f"{data['date_cal']} {data['time']}"
    f_date_time = datetime.strptime(date_time, "%d.%m.%Y %H:%M")

    if data['role'] == 'user':
        flag = await SchMsgsQs.check_time(f_date_time, data['cities'])
    else:
        flag = False

    if flag:
        await callback.message.edit_text(f"Вы выбрали {data['date_cal']}\n\n"
                                         f"<b>К сожалению, время {data['time']} на дату {data['date_cal']} уже занято.</b>\n"
                                         f"Выберите пожалуйста другое время (MSK)!")
        await callback.message.edit_reply_markup(reply_markup=time_picker_kb(callback_data.hour_cur,
                                                                             callback_data.minute_cur))
    elif f_date_time < (datetime.now() + timedelta(minutes=10)):
        try:
            await callback.message.edit_text(f"Вы выбрали {data['date_cal']}\n\n"
                                             f"<b>Выберите пожалуйста время, которое минимум на 10 минут больше нынешнего (MSK)!</b>")
        except:
            pass
        await callback.message.edit_reply_markup(reply_markup=time_picker_kb(callback_data.hour_cur,
                                                                             callback_data.minute_cur))
    else:
        await order_message_lo(callback, state, data)
