from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar

from database.FSM import UserText, UserCities
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from handlers.callback_factories import UserCityStatusCF, PinCF, UserCityCF
from keyboards.user_kbs import example_kb, back_user_text_kb, photo_user_kb, edit_final_kb
from layouts.handlers_layouts import choice_user_first_city, del_messages_lo

router = Router()


@router.callback_query(F.data == 'vacancy')
async def vacancy_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await choice_user_first_city(callback, state, 'vac')


@router.callback_query(F.data == 'ad')
async def ad_country(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await choice_user_first_city(callback, state, 'ad')


@router.message(UserCities.city)
async def city_add(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    data_check = await state.get_data()

    if 'cities' in data_check:
        cities_all = await ChannelsQs.get_cities(data_check['cat'])
        user_cities = data_check['cities'].split()
        cities_list = [city[0] for city in cities_all if city[0] not in user_cities]
    else:
        cities = await ChannelsQs.get_cities(data_check['cat'])
        cities_list = [city[0] for city in cities]

    if msg.text in cities_list:
        await del_messages_lo(msg.from_user.id)

        if 'cities' in data_check:
            await state.update_data(cities=f"{data_check['cities']} {msg.text}")
        else:
            await state.update_data(cities=f'{msg.text}')

        def city_add_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(
                text=f"Продолжить", callback_data=UserCityStatusCF(
                    add=False,
                    next=True
                )
            )
            if len(cities_list) > 1:
                kb.button(
                    text=f"Добавить еще город", callback_data=UserCityStatusCF(
                        add=True,
                        next=False
                    )
                )
            kb.adjust(1)
            return kb.as_markup()

        new_line = '\n'

        data = await state.get_data()

        list_cities = data['cities'].split()

        cities = await ChannelsQs.get_user_cities(list_cities, data['cat'])

        await msg.answer(f"Вы выбрали следующие города:\n"
                                         f"{new_line.join(f'{city[0]} ({city[1]} руб.)' for city in cities)}",
                         reply_markup=city_add_kb())
    else:
        message = await msg.answer(f"Данного города нет в списке, попробуйте ввести название еще раз!")
        await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(UserCityStatusCF.filter(F.add))
async def vacancy_city_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await del_messages_lo(callback.from_user.id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await choice_user_first_city(callback, state, data['cat'])


@router.callback_query(UserCityCF.filter(F.all))
async def all_cities(callback: CallbackQuery, state: FSMContext):
    data_all = await state.get_data()

    cities = await ChannelsQs.get_cities(data_all['cat'])
    cities_all = ' '.join(city[0] for city in cities)

    await state.update_data(cities=cities_all)

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    def city_all_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Продолжить", callback_data=UserCityStatusCF(
                add=False,
                next=True
            )
        )
        kb.adjust(1)
        return kb.as_markup()

    new_line = '\n'

    await callback.message.edit_text(f"Вы выбрали следующие города:\n"
                     f"{new_line.join(f'{city[0]} ({city[1]} руб.)' for city in cities)}")
    await callback.message.edit_reply_markup(reply_markup=city_all_kb())


@router.callback_query(UserCityStatusCF.filter(F.next))
async def city_next(callback: CallbackQuery, state: FSMContext):
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
        kb.adjust(1)
        return kb.as_markup()

    data = await state.get_data()

    if data['cat'] == 'vac':
        await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?\n\n"
                                         f"Стоимость размещения с закреплением:\n"
                                         f" + 300 руб./сутки\n"
                                         f" + 1500 руб./неделя\n"
                                         f" + 3000 руб./месяц")
    elif data['cat'] == 'ad':
        await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?\n\n"
                                         f"Стоимость размещения с закреплением:\n"
                                         f" + 500 руб./сутки\n"
                                         f" + 2000 руб./неделя\n"
                                         f" + 4000 руб./месяц")
    await callback.message.edit_reply_markup(reply_markup=pin_kb())


@router.callback_query(PinCF.filter(F.pin == True))
async def pin_true(callback: CallbackQuery, state: FSMContext, callback_data: PinCF):
    await state.update_data(role='user')

    if callback_data.format == 'day':
        await state.set_state(UserText.pin_day)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(f"Напишите количество дней")
    elif callback_data.format == 'week':
        await state.set_state(UserText.pin_week)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(f"Напишите количество недель")
    elif callback_data.format == 'month':
        await state.set_state(UserText.pin_month)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(f"Напишите количество месяцев")

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.callback_query(PinCF.filter(F.pin == False))
async def pin_false(callback: CallbackQuery, state: FSMContext):
    await state.update_data(role='user', pin=False)
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    await state.set_state(UserText.text)
    data = await state.get_data()

    if data['cat'] == 'vac':
        await callback.message.edit_text("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                         "1. Название должности, заработная плата, адрес:\n"
                                         "2. Обязанности:\n"
                                         "3. Требования:\n"
                                         "4. Мы предлагаем:\n"
                                         "5. Контакты:\n")
        await callback.message.edit_reply_markup(reply_markup=example_kb())
    elif data['cat'] == 'ad':
        await callback.message.delete_reply_markup()
        await callback.message.edit_text("Отправьте боту текст рекламного поста")


@router.message(UserText.pin_day)
async def pin_days(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    try:
        await state.update_data(pin=True, pin_day=int(msg.text))
        await state.set_state(UserText.text)

        data = await state.get_data()

        if data['cat'] == 'vac':
            await state.update_data(pin_sum=data['pin_day'] * 300)
            message = await msg.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                       "1. Название должности, заработная плата, адрес:\n"
                                       "2. Обязанности:\n"
                                       "3. Требования:\n"
                                       "4. Мы предлагаем:\n"
                                       "5. Контакты:\n", reply_markup=example_kb())
        else:
            await state.update_data(pin_sum=data['pin_day'] * 500)
            message = await msg.answer("Отправьте боту текст рекламного поста")
    except ValueError:
        await state.set_state(UserText.pin_day)
        message = await msg.answer('Введите количество дней')

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(UserText.pin_week)
async def pin_week(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    try:
        await state.update_data(pin=True, pin_week=int(msg.text))

        await state.set_state(UserText.text)

        data = await state.get_data()

        if data['cat'] == 'vac':
            await state.update_data(pin_sum=data['pin_week']*1500)
            message = await msg.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                       "1. Название должности, заработная плата, адрес:\n"
                                       "2. Обязанности:\n"
                                       "3. Требования:\n"
                                       "4. Мы предлагаем:\n"
                                       "5. Контакты:\n", reply_markup=example_kb())
        else:
            await state.update_data(pin_sum=data['pin_week'] * 2000)
            message = await msg.answer("Отправьте боту текст рекламного поста")
    except ValueError:
        await state.set_state(UserText.pin_week)
        message = await msg.answer('Введите количество недель')

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(UserText.pin_month)
async def pin_month(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    try:
        await state.update_data(pin=True, pin_month=int(msg.text))
        await state.set_state(UserText.text)

        data = await state.get_data()

        if data['cat'] == 'vac':
            await state.update_data(pin_sum=data['pin_month'] * 3000)
            message = await msg.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                       "1. Название должности, заработная плата, адрес:\n"
                                       "2. Обязанности:\n"
                                       "3. Требования:\n"
                                       "4. Мы предлагаем:\n"
                                       "5. Контакты:\n", reply_markup=example_kb())
        else:
            await state.update_data(pin_sum=data['pin_month'] * 4000)
            message = await msg.answer("Отправьте боту текст рекламного поста")
    except ValueError:
        await state.set_state(UserText.pin_week)
        message = await msg.answer('Введите количество недель')

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

