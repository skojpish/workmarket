from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar

from database.FSM import UserText, UserCities, MsgAllChannels
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from database.package_pins import PackagePinsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import UserCityStatusCF, PinCF, UserCityCF, PackagesCF, PinPackagesCF
from keyboards.time_picker import time_picker_kb
from keyboards.user_kbs import example_kb, back_user_text_kb, photo_user_kb, edit_final_kb, package_confirm_kb, \
    pin_package_confirm_kb, time_manually_kb, time_manually_confirm_kb
from layouts.handlers_layouts import choice_user_first_city, del_messages_lo, pin_lo

router = Router()


@router.callback_query(F.data == 'vacancy')
async def vacancy_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(role='user')
    await choice_user_first_city(callback, state, 'vac', 0)


@router.callback_query(F.data == 'ad')
async def ad_country(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(role='user')
    await choice_user_first_city(callback, state, 'ad', 0)


@router.message(UserCities.city)
async def city_add(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    data_check = await state.get_data()

    if 'cities' in data_check:
        cities_all = await ChannelsQs.get_all_cities(data_check['cat'])
        user_cities = data_check['cities'].split(',')
        cities_list = [city[0] for city in cities_all if city[0] not in user_cities]
    else:
        cities = await ChannelsQs.get_all_cities(data_check['cat'])
        cities_list = [city[0] for city in cities]

    user_msg_list = msg.text.split(', ')

    if any(city in user_msg_list for city in cities_list):
        for entered_city in user_msg_list:
            if entered_city in cities_list:
                data = await state.get_data()
                if 'cities' in data:
                    await state.update_data(cities=f"{data['cities']},{entered_city}")
                else:
                    await state.update_data(cities=f'{entered_city}')
                cities_list.remove(entered_city)

        def city_add_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(
                text=f"Продолжить", callback_data=UserCityStatusCF(
                    add=False,
                    next=True,
                    starting_point=0,
                    back=False
                )
            )
            if len(cities_list) > 0:
                kb.button(
                    text=f"Добавить еще город", callback_data=UserCityStatusCF(
                        add=True,
                        next=False,
                        starting_point=0,
                        back=False
                    )
                )
            kb.adjust(1)
            return kb.as_markup()

        new_line = '\n'

        data = await state.get_data()

        list_cities = data['cities'].split(',')

        cities = await ChannelsQs.get_user_cities(list_cities, data['cat'])

        await msg.answer(f"Вы выбрали следующие города:\n"
                              f"{new_line.join(f'{city[0]} ({city[1]} руб.)' for city in cities)}",
                         reply_markup=city_add_kb())
        await del_messages_lo(msg.from_user.id)
    else:
        message = await msg.answer(f"Данного города нет в списке, попробуйте ввести название еще раз!")
        await state.set_state(UserCities.city)
        await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(UserCityStatusCF.filter(F.add))
async def vacancy_city_add(callback: CallbackQuery, callback_data: UserCityStatusCF, state: FSMContext):
    data = await state.get_data()
    await choice_user_first_city(callback, state, data['cat'], callback_data.starting_point)
    if callback_data.starting_point == 0 and not callback_data.back:
        await del_messages_lo(callback.from_user.id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == 'packages')
async def packages(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    def packages_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Купить пакет публикаций",
            callback_data='buy_package'
        )
        if data['cat'] == 'vac':
            kb.button(
                text=f"Разместить вакансию",
                callback_data="vacancy"
            )
        else:
            kb.button(
                text=f"Разместить рекламу",
                callback_data="ad"
            )
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Для наших постоянных клиентов действуют скидки на пакетное размещение "
                                     "во всех городах.\n"
                                     "Вы сможете приобрести пакеты для ежемесячного размещения публикаций.\n"
                                     "В течение 30 дней после покупки вы должны использовать пакет публикаций, "
                                     "за истечением 30 дневного срока пакет автоматически будет аннулирован.\n\n"
                                     "Пакет 1: 2 публикации - скидка 50%\n"
                                     "Пакет 2: 3 публикации - скидка 60% \n"
                                     "Пакет 3: 4 публикации - скидка 70% \n"
                                     "Пакет 4: 5 публикаций - скидка 80%\n"
                                     "Пакет 5: 10 публикаций - скидка 90%\n"
                                     "Пакет 6: 15 публикаций - скидка 95%")
    await callback.message.edit_reply_markup(reply_markup=packages_kb())


@router.callback_query(F.data == 'buy_package')
async def buy_package(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    package_1 = '{:g}'.format(data['all_cities_sum'] * 0.5 * 2)
    package_2 = '{:g}'.format(data['all_cities_sum'] * 0.4 * 3)
    package_3 = '{:g}'.format(data['all_cities_sum'] * 0.3 * 4)
    package_4 = '{:g}'.format(data['all_cities_sum'] * 0.2 * 5)
    package_5 = '{:g}'.format(data['all_cities_sum'] * 0.1 * 10)
    package_6 = '{:g}'.format(data['all_cities_sum'] * 0.05 * 15)

    def buy_package_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Пакет 1",
            callback_data=PackagesCF(package_num=1, package_sum=int(package_1), publ_count=2)
        )
        kb.button(
            text=f"Пакет 2",
            callback_data=PackagesCF(package_num=2, package_sum=int(package_2), publ_count=3)
        )
        kb.button(
            text=f"Пакет 3",
            callback_data=PackagesCF(package_num=3, package_sum=int(package_3), publ_count=4)
        )
        kb.button(
            text=f"Пакет 4",
            callback_data=PackagesCF(package_num=4, package_sum=int(package_4), publ_count=5)
        )
        kb.button(
            text=f"Пакет 5",
            callback_data=PackagesCF(package_num=5, package_sum=int(package_5), publ_count=10)
        )
        kb.button(
            text=f"Пакет 6",
            callback_data=PackagesCF(package_num=6, package_sum=int(package_6), publ_count=15)
        )
        kb.button(
            text=f"Назад",
            callback_data="packages"
        )
        kb.adjust(2)
        return kb.as_markup()

    await callback.message.edit_text("<b>Стоимость пакетов</b>\n\n"
                                     f"Пакет 1: 2 публикации - скидка 50% (<s>{data['all_cities_sum'] * 2}</s> {package_1} руб.)\n"
                                     f"Пакет 2: 3 публикации - скидка 60% (<s>{data['all_cities_sum'] * 3}</s> {package_2} руб.)\n"
                                     f"Пакет 3: 4 публикации - скидка 70% (<s>{data['all_cities_sum'] * 4}</s> {package_3} руб.)\n"
                                     f"Пакет 4: 5 публикаций - скидка 80% (<s>{data['all_cities_sum'] * 5}</s> {package_4} руб.)\n"
                                     f"Пакет 5: 10 публикаций - скидка 90% (<s>{data['all_cities_sum'] * 10}</s> {package_5} руб.)\n"
                                     f"Пакет 6: 15 публикаций - скидка 95% (<s>{data['all_cities_sum'] * 15}</s> {package_6} руб.)\n\n"
                                     f"Выберите один из пакетов")
    await callback.message.edit_reply_markup(reply_markup=buy_package_kb())


@router.callback_query(PackagesCF.filter())
async def buy_package_cf(callback: CallbackQuery, callback_data: PackagesCF, state: FSMContext):
    await state.update_data(package_sum=callback_data.package_sum, publ_count=callback_data.publ_count)
    if callback_data.publ_count < 5:
        await callback.message.edit_text(f"Вы выбрали:\n"
                                         f"Пакет {callback_data.package_num}: {callback_data.publ_count} публикации за "
                                         f"{callback_data.package_sum} руб.")
    else:
        await callback.message.edit_text(f"Вы выбрали:\n"
                                         f"Пакет {callback_data.package_num}: {callback_data.publ_count} публикаций за "
                                         f"{callback_data.package_sum} руб.")
    await callback.message.edit_reply_markup(reply_markup=package_confirm_kb())


@router.callback_query(UserCityCF.filter(F.all))
async def all_cities(callback: CallbackQuery, state: FSMContext):
    data_all = await state.get_data()

    cities = await ChannelsQs.get_all_cities(data_all['cat'])
    cities_all = ','.join(city[0] for city in cities)

    await state.update_data(cities=cities_all, all_cities='Все российские города в сети WorkMarket')

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    def city_all_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Продолжить", callback_data=UserCityStatusCF(
                add=False,
                next=True,
                starting_point=0,
                back=False
            )
        )
        kb.adjust(1)
        return kb.as_markup()

    data = await state.get_data()

    await callback.message.edit_text(f"Вы выбрали следующие города:\n"
                     f"{data['all_cities']}")
    await callback.message.edit_reply_markup(reply_markup=city_all_kb())


@router.callback_query(UserCityStatusCF.filter(F.next))
async def city_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    users_pckg_info = await PackagePinsQs.get_user(callback.from_user.id)

    try:
        if users_pckg_info[0] and users_pckg_info[1] == data['cat']:
            def package_kb() -> InlineKeyboardMarkup:
                kb = InlineKeyboardBuilder()
                kb.button(
                    text=f"Закрепить на месяц",
                    callback_data=PinCF(pin=False, format='pin_package')
                )
                kb.button(
                    text=f"Не закреплять",
                    callback_data=PinCF(pin=False, format='')
                )
                kb.adjust(1)
                return kb.as_markup()

            await callback.message.edit_text(f"У вас осталось <b>{users_pckg_info[0]}</b> закреплений на месяц")
            await callback.message.edit_reply_markup(reply_markup=package_kb())
        else:
            await pin_lo(callback, data['cat'])
    except TypeError:
        await pin_lo(callback, data['cat'])


@router.callback_query(F.data == 'packages_pin')
async def packages_pin(callback: CallbackQuery):
    def packages_pin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Купить пакет закреплений",
            callback_data='buy_pin_package'
        )
        kb.button(
            text=f"Назад",
            callback_data=UserCityStatusCF(next=True, add=False, starting_point=0, back=False)
        )
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Для наших постоянных клиентов действуют скидки на одномесячное пакетное "
                                     "закрепление постов.\n"
                                     "Вы сможете приобрести пакеты для закрепления публикаций на один месяц.\n"
                                     "В течение 30 дней после покупки вы должны использовать пакет закреплений, "
                                     "за истечением 30 дневного срока пакет автоматически будет аннулирован.\n\n"
                                     "Пакет 1: 2 закрепления - скидка 50%\n"
                                     "Пакет 2: 3 закрепления - скидка 60% \n"
                                     "Пакет 3: 4 закрепления - скидка 70% \n"
                                     "Пакет 4: 5 закреплений - скидка 80%\n"
                                     "Пакет 5: 10 закреплений - скидка 90%\n"
                                     "Пакет 6: 15 закреплений - скидка 95%")
    await callback.message.edit_reply_markup(reply_markup=packages_pin_kb())


@router.callback_query(F.data == 'buy_pin_package')
async def buy_pin_package(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data['cat'] == 'vac':
        pin_package_sum = 3000
    else:
        pin_package_sum = 4000

    package_1 = '{:g}'.format(pin_package_sum * 0.5 * 2)
    package_2 = '{:g}'.format(pin_package_sum * 0.4 * 3)
    package_3 = '{:g}'.format(pin_package_sum * 0.3 * 4)
    package_4 = '{:g}'.format(pin_package_sum * 0.2 * 5)
    package_5 = '{:g}'.format(pin_package_sum * 0.1 * 10)
    package_6 = '{:g}'.format(pin_package_sum * 0.05 * 15)

    def buy_pin_package_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Пакет 1",
            callback_data=PinPackagesCF(package_num=1, package_sum=int(package_1), pin_count=2)
        )
        kb.button(
            text=f"Пакет 2",
            callback_data=PinPackagesCF(package_num=2, package_sum=int(package_2), pin_count=3)
        )
        kb.button(
            text=f"Пакет 3",
            callback_data=PinPackagesCF(package_num=3, package_sum=int(package_3), pin_count=4)
        )
        kb.button(
            text=f"Пакет 4",
            callback_data=PinPackagesCF(package_num=4, package_sum=int(package_4), pin_count=5)
        )
        kb.button(
            text=f"Пакет 5",
            callback_data=PinPackagesCF(package_num=5, package_sum=int(package_5), pin_count=10)
        )
        kb.button(
            text=f"Пакет 6",
            callback_data=PinPackagesCF(package_num=6, package_sum=int(package_6), pin_count=15)
        )
        kb.button(
            text=f"Назад",
            callback_data="packages_pin"
        )
        kb.adjust(2)
        return kb.as_markup()

    await callback.message.edit_text("<b>Стоимость пакетов</b>\n\n"
                                     f"Пакет 1: 2 закрепления - скидка 50% (<s>{pin_package_sum * 2}</s> {package_1} руб.)\n"
                                     f"Пакет 2: 3 закрепления - скидка 60% (<s>{pin_package_sum * 3}</s> {package_2} руб.)\n"
                                     f"Пакет 3: 4 закрепления - скидка 70% (<s>{pin_package_sum * 4}</s> {package_3} руб.)\n"
                                     f"Пакет 4: 5 закреплений - скидка 80% (<s>{pin_package_sum * 5}</s> {package_4} руб.)\n"
                                     f"Пакет 5: 10 закреплений - скидка 90% (<s>{pin_package_sum * 10}</s> {package_5} руб.)\n"
                                     f"Пакет 6: 15 закреплений - скидка 95% (<s>{pin_package_sum * 15}</s> {package_6} руб.)\n\n"
                                     f"Выберите один из пакетов")
    await callback.message.edit_reply_markup(reply_markup=buy_pin_package_kb())


@router.callback_query(PinPackagesCF.filter())
async def buy_pin_package_cf(callback: CallbackQuery, callback_data: PinPackagesCF, state: FSMContext):
    await state.update_data(pin_package_sum=callback_data.package_sum, pin_count=callback_data.pin_count)
    if callback_data.pin_count < 5:
        await callback.message.edit_text(f"Вы выбрали:\n"
                                         f"Пакет {callback_data.package_num}: {callback_data.pin_count} закрепления за "
                                         f"{callback_data.package_sum} руб.")
    else:
        await callback.message.edit_text(f"Вы выбрали:\n"
                                         f"Пакет {callback_data.package_num}: {callback_data.pin_count} закреплений за "
                                         f"{callback_data.package_sum} руб.")
    await callback.message.edit_reply_markup(reply_markup=pin_package_confirm_kb())


@router.callback_query(PinCF.filter(F.pin == True))
async def pin_true(callback: CallbackQuery, state: FSMContext, callback_data: PinCF):
    await state.set_state(UserText.pin)
    await callback.message.delete_reply_markup()

    if callback_data.format == 'day':
        await state.update_data(pin_day=True)
        await callback.message.edit_text(f"Напишите количество дней")
    elif callback_data.format == 'week':
        await state.update_data(pin_week=True)
        await callback.message.edit_text(f"Напишите количество недель")
    else:
        await state.update_data(pin_month=True)
        await callback.message.edit_text(f"Напишите количество месяцев")

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.callback_query(PinCF.filter(F.pin == False))
async def pin_false(callback: CallbackQuery, callback_data: PinCF, state: FSMContext):
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    data = await state.get_data()

    if data['role'] == 'user':
        if callback_data.format == 'pin_package':
            await state.update_data(pin=True, pin_month=1)
        else:
            await state.update_data(pin=False)

        await state.set_state(UserText.text)

        if data['cat'] == 'vac':
            await callback.message.edit_text("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                             "1. Название должности, заработная плата, адрес:\n"
                                             "2. Обязанности:\n"
                                             "3. Требования:\n"
                                             "4. Мы предлагаем:\n"
                                             "5. Контакты:\n")
            await callback.message.edit_reply_markup(reply_markup=example_kb())
        else:
            await callback.message.delete_reply_markup()
            await callback.message.edit_text("Отправьте боту текст рекламного поста")
    else:
        await state.update_data(pin=False)
        await state.set_state(MsgAllChannels.text)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text("Напишите текст сообщения")


@router.message(UserText.pin)
async def pin_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    data = await state.get_data()

    try:
        if data['role'] == 'user':
            await state.set_state(UserText.text)

            if data['cat'] == 'vac':
                if 'pin_day' in data:
                    await state.update_data(pin=True, pin_day=int(msg.text), pin_sum=int(msg.text) * 300)
                elif 'pin_week' in data:
                    await state.update_data(pin=True, pin_week=int(msg.text), pin_sum=int(msg.text) * 1500)
                else:
                    await state.update_data(pin=True, pin_month=int(msg.text), pin_sum=int(msg.text) * 3000)

                message = await msg.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                           "1. Название должности, заработная плата, адрес:\n"
                                           "2. Обязанности:\n"
                                           "3. Требования:\n"
                                           "4. Мы предлагаем:\n"
                                           "5. Контакты:\n", reply_markup=example_kb())
            else:
                if 'pin_day' in data:
                    await state.update_data(pin=True, pin_day=int(msg.text), pin_sum=int(msg.text) * 500)
                elif 'pin_week' in data:
                    await state.update_data(pin=True, pin_week=int(msg.text), pin_sum=int(msg.text) * 2000)
                else:
                    await state.update_data(pin=True, pin_month=int(msg.text), pin_sum=int(msg.text) * 4000)
                message = await msg.answer("Отправьте боту текст рекламного поста")
        else:
            await state.set_state(MsgAllChannels.text)
            if 'pin_day' in data:
                await state.update_data(pin=True, pin_day=int(msg.text))
            elif 'pin_week' in data:
                await state.update_data(pin=True, pin_week=int(msg.text))
            else:
                await state.update_data(pin=True, pin_month=int(msg.text))
            message = await msg.answer("Напишите текст сообщения")
    except ValueError:
        await state.set_state(UserText.pin)
        if 'pin_day' in data:
            message = await msg.answer('Введите количество дней')
        elif 'pin_week' in data:
            message = await msg.answer('Введите количество недель')
        else:
            message = await msg.answer('Введите количество месяцев')

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(F.data == 'example')
async def example(callback: CallbackQuery):
    await callback.message.edit_text("Кассир-операционист (метро Пражская)\n"
                                     "От 50 000 ₽ на руки\n\n"
                                     "Обязанности:\n"
                                     "• Кассовое обслуживание физических лиц\n"
                                     "• Валютно-обменные операции\n"
                                     "• Денежные переводы без открытия счета\n"
                                     "• Прием платежей\n"
                                     "• Инкассация\n"
                                     "• Отчетность\n\n"
                                     "Требования:\n"
                                     "• Образование не ниже среднего специального\n"
                                     "• Опыт работы с денежной наличностью в любой сфере\n"
                                     "• Уверенное владение ПК\n"
                                     "• Навыки работы с сетью Интернет\n"
                                     "• Грамотная устная и письменная речь на русском языке\n"
                                     "• Общительность, доброжелательность, готовность к обучению\n\n"
                                     "Мы предлагаем:\n"
                                     "• Оформление в штат в соответствии с ТК РФ\n"
                                     "• Профессиональное обучение\n"
                                     "• График работы 2/2\n"
                                     "• Фитнес и корпоративные скидки\n"
                                     "• Участие в спортивных мероприятиях\n"
                                     "• Поддержку куратора\n"
                                     "• Профессиональный и карьерный рост\n\n"
                                     "Контакты:\n"
                                     "+74952270179\n"
                                     "e.zaharova@unistream.com\n")
    await callback.message.edit_reply_markup(reply_markup=back_user_text_kb())


@router.callback_query(F.data == 'user_text_back')
async def user_text_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserText.text)

    await callback.message.edit_text("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                     "1. Название должности, заработная плата, адрес:\n"
                                     "2. Обязанности:\n"
                                     "3. Требования:\n"
                                     "4. Мы предлагаем:\n"
                                     "5. Контакты:")
    await callback.message.edit_reply_markup(reply_markup=example_kb())


@router.message(UserText.text)
async def user_text(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(text=msg.text)
    data = await state.get_data()

    if 'edit' in data:
        message = await msg.answer("Текст сообщения успешно изменен!", reply_markup=edit_final_kb())
    else:
        await state.set_state(UserText.photo)

        message = await msg.answer("Отправьте фото к посту", reply_markup=photo_user_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(UserText.photo)
async def user_photo(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    if msg.photo:
        await state.update_data(photo=msg.photo[-1].file_id)
        data = await state.get_data()

        if 'edit' in data:
            message = await msg.answer("Фото успешно изменено!", reply_markup=edit_final_kb())
        else:
            message = await msg.answer("Выберите дату публикации", reply_markup=await SimpleCalendar().start_calendar())
    else:
        await state.set_state(UserText.photo)
        message = await msg.answer("Отправьте фото к посту", reply_markup=photo_user_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(F.data == 'without_photo_user')
async def without_photo(callback: CallbackQuery):
    await callback.message.edit_text("Выберите дату публикации")
    await callback.message.edit_reply_markup(reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(F.data == 'time_manually')
async def time_manually(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(UserText.time_manually)
    await callback.message.edit_text(f"Вы выбрали {data['date_cal']}\n\n"
                                     f"Напишите время публикации в формате ЧЧ:ММ (MSK)")
    await callback.message.edit_reply_markup(reply_markup=time_manually_kb())


@router.callback_query(F.data == 'time_back')
async def time_picker_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'time_manually' in data:
        await state.update_data(time_manually=False)
    await callback.message.edit_text(f"Вы выбрали {data['date_cal']}\n\n"
                                     f"Выберите время публикации (MSK)")
    await callback.message.edit_reply_markup(reply_markup=time_picker_kb(12, 0))


@router.message(UserText.time_manually)
async def time_manually_entered(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    time_list = msg.text.split(':')

    if (len(time_list) == 2) and (int(time_list[0]) in range(24)) and (int(time_list[1]) in range(60)) \
            and (len(time_list[0]) == 2) and (len(time_list[1]) == 2):
        await state.update_data(time=f'{time_list[0]}:{time_list[1]}', time_manually=True)
        data = await state.get_data()

        date_time = f"{data['date_cal']} {data['time']}"
        f_date_time = datetime.strptime(date_time, "%d.%m.%Y %H:%M")

        if data['role'] == 'user':
            flag = await SchMsgsQs.check_time(f_date_time, data['cities'])
        else:
            flag = False

        if flag:
            message = await msg.answer(f"<b>К сожалению, время {data['time']} на дату {data['date_cal']} уже занято.</b>\n"
                             f"Напишите пожалуйста другое время (MSK)!")
            await state.set_state(UserText.time_manually)
        elif f_date_time < (datetime.now() + timedelta(minutes=10)):
            message = await msg.answer(f"<b>Напишите пожалуйста время, которое минимум на 10 минут больше нынешнего (MSK)!</b>")
            await state.set_state(UserText.time_manually)
        else:
            message = await msg.answer(f"Вы выбрали время {data['time']} на дату {data['date_cal']}",
                                       reply_markup=time_manually_confirm_kb())
    else:
        message = await msg.answer("<b>Вы ввели время в неправильном формате!</b>\n"
                             "Необходимый формат: ЧЧ:ММ (MSK)\n"
                             "Попробуйте еще раз!")
        await state.set_state(UserText.time_manually)

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)
